"""
ROADFM 시연용 관광지 데이터 수집 스크립트 (서울 → 강릉 3개 경로)

- 경로를 따라 일정 간격으로 지점을 찍고, 각 지점 주변 관광지를 TourAPI(KorService2)로 조회한다.
- 프로토타입에 나오는 장소는 키워드 검색으로 반드시 포함한다.
- 장소마다 개요(overview)·소개정보(운영시간/휴무/주차)를 받아 '짧은 안내 문장'을 만든다.
- 오디(Odii) 이야기(대본·음원)가 근처에 있으면 함께 붙인다.

인증키: 환경변수 TOUR_API_KEY 또는 실행 시 입력. 파일/코드에 저장하지 않는다.
API 응답은 .cache/ 에 저장해서, 다시 실행해도 같은 호출을 반복하지 않는다(일일 트래픽 절약).

실행:  python -I tools/collect_places/collect_places.py
옵션:  --dry-run (호출 없이 계획만 출력), --no-odii, --no-detail
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import html
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://apis.data.go.kr/B551011"
HERE = Path(__file__).resolve().parent
CACHE_DIR = HERE / ".cache"
OUT_DIR = HERE / "output"

# ── 설정 ────────────────────────────────────────────────────────────────
STEP_KM = 25            # 경로 위 조회 지점 간격
RADIUS_M = 8000         # 지점별 조회 반경 (최대 20000)
ROWS_PER_POINT = 10     # 지점·유형별 가져올 개수 (거리순)
SKIP_NEAR_START_KM = 20 # 출발지(서울 도심) 근처는 건너뜀
CONTENT_TYPES = {"12": "관광지", "14": "문화시설"}
ODII_MATCH_M = 500      # 오디 이야기를 관광지에 붙일 최대 거리

# 경로 좌표는 대략적인 경유 도시 기준(lat, lng). 실제 도로 경로는 추후 외부 길찾기 API로 대체.
ROUTES = [
    {
        "id": "fast", "title": "빠른 길", "desc": "영동고속도로 중심",
        "points": [(37.5665, 126.9780), (37.2800, 127.1100), (37.2720, 127.4350), (37.2980, 127.6370),
                   (37.3420, 127.9200), (37.4300, 128.1200), (37.5600, 128.4200), (37.6850, 128.7200),
                   (37.7519, 128.8961)],
    },
    {
        "id": "scenic", "title": "풍경 좋은 길", "desc": "양평·홍천 경유",
        "points": [(37.5665, 126.9780), (37.5350, 127.3180), (37.4910, 127.4880), (37.6970, 127.8880),
                   (37.7860, 127.9710), (37.6200, 128.3600), (37.6850, 128.7200), (37.7519, 128.8961)],
    },
    {
        "id": "culture", "title": "문화가 깃든 길", "desc": "원주·횡성 경유",
        "points": [(37.5665, 126.9780), (37.4150, 127.8250), (37.3420, 127.9200), (37.3700, 128.0500),
                   (37.4910, 127.9850), (37.5600, 128.4200), (37.6850, 128.7200), (37.7519, 128.8961)],
    },
]

# 프로토타입(prototype2)에 등장하는 장소 — 반드시 포함 시도
MUST_INCLUDE = [
    "대관령 양떼목장", "경포호", "강릉솔향수목원", "횡성 한우", "봉평", "안목 커피거리", "오죽헌",
    "대관령박물관", "선교장", "두물머리", "수타사", "치악산", "숲체원", "원주 중앙시장",
    "초당 순두부", "뮤지엄 SAN", "원주 역사박물관", "강릉향교",
]


# ── 유틸 ────────────────────────────────────────────────────────────────
def haversine_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lng1, lat2, lng2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def sample_route(points: list[tuple[float, float]], step_km: float) -> list[tuple[float, float]]:
    """경로 폴리라인을 step_km 간격으로 샘플링 (선형 보간)."""
    out = [points[0]]
    carry = 0.0
    for a, b in zip(points, points[1:]):
        seg = haversine_m(a, b) / 1000
        d = step_km - carry
        while d <= seg:
            t = d / seg
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            d += step_km
        carry = seg - (d - step_km)
    if out[-1] != points[-1]:
        out.append(points[-1])
    return out


def clean_text(s: str | None) -> str:
    if not s:
        return ""
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def first_sentence(text: str, max_len: int = 90) -> str:
    m = re.search(r"^(.+?[다요음함임][.!])(\s|$)", text) or re.search(r"^(.+?[.!?])(\s|$)", text)
    s = m.group(1) if m else text
    return s if len(s) <= max_len else s[: max_len - 1].rstrip() + "…"


def as_list(items) -> list[dict]:
    if not items:
        return []
    return items if isinstance(items, list) else [items]


# ── API 호출 ────────────────────────────────────────────────────────────
class Api:
    def __init__(self, key: str | None, dry_run: bool):
        self.dry_run = dry_run
        self.calls = 0
        self.cache_hits = 0
        # Encoding 키(이미 %인코딩)는 그대로, Decoding 키는 인코딩해서 사용
        self.key_q = (key if "%" in key else urllib.parse.quote(key, safe="")) if key else ""
        CACHE_DIR.mkdir(exist_ok=True)

    def get(self, path: str, **params) -> list[dict]:
        common = {"MobileOS": "ETC", "MobileApp": "ROADFM", "_type": "json"}
        q = urllib.parse.urlencode({**common, **params})
        cache_file = CACHE_DIR / (hashlib.sha1(f"{path}?{q}".encode()).hexdigest() + ".json")
        if cache_file.exists():
            self.cache_hits += 1
            return json.loads(cache_file.read_text(encoding="utf-8"))
        if self.dry_run:
            self.calls += 1
            return []

        url = f"{BASE}/{path}?serviceKey={self.key_q}&{q}"
        for attempt in range(3):
            try:
                with urllib.request.urlopen(url, timeout=20) as r:
                    body = r.read().decode("utf-8")
                break
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt == 2:
                    raise SystemExit(f"[네트워크 오류] {path}: {e}")
                time.sleep(1.5)
        self.calls += 1
        time.sleep(0.15)

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            # 인증 오류 등은 XML로 온다
            msg = re.search(r"<returnAuthMsg>(.*?)</returnAuthMsg>|<resultMsg>(.*?)</resultMsg>", body)
            text = next((g for g in (msg.groups() if msg else []) if g), body[:200])
            raise SystemExit(f"[API 오류] {path}: {text}\n→ 인증키(Encoding/Decoding)·활용신청 승인 여부를 확인하세요.")

        header = data.get("response", {}).get("header", {})
        if header.get("resultCode") not in ("0000", "00", None):
            raise SystemExit(f"[API 오류] {path}: {header.get('resultCode')} {header.get('resultMsg')}")
        body_ = data.get("response", {}).get("body", {}) or {}
        items = as_list((body_.get("items") or {}).get("item") if isinstance(body_.get("items"), dict) else None)
        cache_file.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
        return items


# ── 수집 ────────────────────────────────────────────────────────────────
def collect(api: Api, use_detail: bool, use_odii: bool) -> dict:
    start = ROUTES[0]["points"][0]
    places: dict[str, dict] = {}
    route_points = {}

    # 1) 경로 주변 위치기반 조회
    for route in ROUTES:
        pts = [p for p in sample_route(route["points"], STEP_KM) if haversine_m(p, start) > SKIP_NEAR_START_KM * 1000]
        route_points[route["id"]] = pts
        print(f"[경로] {route['title']}: 조회 지점 {len(pts)}개")
        for lat, lng in pts:
            for ctype in CONTENT_TYPES:
                for it in api.get("KorService2/locationBasedList2", mapX=f"{lng:.6f}", mapY=f"{lat:.6f}",
                                  radius=RADIUS_M, contentTypeId=ctype, arrange="E",
                                  numOfRows=ROWS_PER_POINT, pageNo=1):
                    p = places.setdefault(str(it["contentid"]), {"raw": it, "routeIds": set(), "mustInclude": False})
                    p["routeIds"].add(route["id"])

    # 2) 프로토타입 장소 키워드 검색
    for kw in MUST_INCLUDE:
        hits = api.get("KorService2/searchKeyword2", keyword=kw, numOfRows=5, pageNo=1)
        hit = next((h for h in hits if kw.replace(" ", "") in h.get("title", "").replace(" ", "")), hits[0] if hits else None)
        if hit:
            p = places.setdefault(str(hit["contentid"]), {"raw": hit, "routeIds": set(), "mustInclude": False})
            p["mustInclude"] = True
        elif not api.dry_run:
            print(f"  ! 키워드 결과 없음: {kw}")

    # 각 장소에 가장 가까운 경로 지정 (키워드로만 들어온 장소 포함)
    for p in places.values():
        loc = (float(p["raw"].get("mapy") or 0), float(p["raw"].get("mapx") or 0))
        dists = {rid: min(haversine_m(loc, q) for q in pts) for rid, pts in route_points.items() if pts}
        p["distanceFromRouteM"] = round(min(dists.values())) if dists else None
        if not p["routeIds"] and dists:
            p["routeIds"].add(min(dists, key=dists.get))

    print(f"[관광지] 후보 {len(places)}곳")

    # 3) 상세: 개요 + 소개정보
    if use_detail:
        for i, (cid, p) in enumerate(places.items(), 1):
            ctype = str(p["raw"].get("contenttypeid", "12"))
            common = api.get("KorService2/detailCommon2", contentId=cid)
            intro = api.get("KorService2/detailIntro2", contentId=cid, contentTypeId=ctype)
            p["common"] = common[0] if common else {}
            p["intro"] = intro[0] if intro else {}
            if i % 20 == 0:
                print(f"  상세 {i}/{len(places)}")

    # 4) 오디 이야기
    stories: dict[str, dict] = {}
    if use_odii:
        for pts in route_points.values():
            for lat, lng in pts:
                for s in api.get("Odii/storyLocationBasedList", langCode="ko", mapX=f"{lng:.6f}", mapY=f"{lat:.6f}",
                                 radius=RADIUS_M, numOfRows=50, pageNo=1):
                    sid = str(s.get("stid") or s.get("stlid") or s.get("title"))
                    stories.setdefault(sid, s)
        print(f"[오디] 이야기 {len(stories)}건")

    return {"places": places, "stories": stories}


def pick(d: dict, *keys: str) -> str:
    for k in keys:
        v = clean_text(d.get(k))
        if v:
            return v
    return ""


def build_output(res: dict) -> dict:
    out_places, used_story_ids = [], set()
    stories = res["stories"]

    for cid, p in res["places"].items():
        raw, common, intro = p["raw"], p.get("common", {}), p.get("intro", {})
        lat, lng = float(raw.get("mapy") or 0), float(raw.get("mapx") or 0)
        overview = clean_text(common.get("overview"))
        summary = first_sentence(overview) if overview else ""
        usetime = pick(intro, "usetime", "usetimeculture")
        restdate = pick(intro, "restdate", "restdateculture")
        parking = pick(intro, "parking", "parkingculture")
        fee = pick(intro, "usefee")

        # 근처 오디 이야기 연결
        near = []
        for sid, s in stories.items():
            sx, sy = s.get("mapX") or s.get("mapx"), s.get("mapY") or s.get("mapy")
            if sx and sy and haversine_m((lat, lng), (float(sy), float(sx))) <= ODII_MATCH_M:
                near.append(s)
                used_story_ids.add(sid)

        bits = [raw.get("title", "")]
        if summary:
            bits.append(summary)
        tail = []
        if parking:
            tail.append(f"주차 {parking[:20]}")
        if restdate:
            tail.append(f"휴무 {restdate[:20]}")
        guide_short = ". ".join(b.rstrip(".") for b in bits) + "." + (f" {', '.join(tail)}." if tail else "")

        out_places.append({
            "contentId": cid,
            "contentType": CONTENT_TYPES.get(str(raw.get("contenttypeid")), str(raw.get("contenttypeid"))),
            "title": raw.get("title", ""),
            "address": raw.get("addr1", ""),
            "lat": lat, "lng": lng,
            "routeIds": sorted(p["routeIds"]),
            "distanceFromRouteM": p.get("distanceFromRouteM"),
            "fromPrototype": p["mustInclude"],
            "summary": summary,
            "guideShort": guide_short,
            "overview": overview,
            "usetime": usetime, "restdate": restdate, "parking": parking, "fee": fee,
            "image": raw.get("firstimage") or common.get("firstimage") or "",
            "imageLicense": raw.get("cpyrhtDivCd") or common.get("cpyrhtDivCd") or "",
            "odiiStories": near,
        })

    out_places.sort(key=lambda x: (not x["fromPrototype"], x["routeIds"], x["distanceFromRouteM"] or 0))
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "한국관광공사 TourAPI(KorService2), 관광지 오디오 가이드정보(Odii) — 공공데이터포털",
        "note": "시연용 데이터. 경로 좌표는 경유 도시 기준 근사치이며 실제 도로 경로가 아님.",
        "routes": [{"id": r["id"], "title": r["title"], "desc": r["desc"], "points": r["points"]} for r in ROUTES],
        "places": out_places,
        "unmatchedOdiiStories": [s for sid, s in res["stories"].items() if sid not in used_story_ids],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="ROADFM 시연용 관광지 데이터 수집")
    ap.add_argument("--dry-run", action="store_true", help="API 호출 없이 예상 호출 수만 출력")
    ap.add_argument("--no-detail", action="store_true", help="개요·소개정보 조회 생략")
    ap.add_argument("--no-odii", action="store_true", help="오디 이야기 조회 생략")
    ap.add_argument("--out", default=str(OUT_DIR / "places_seoul_gangneung.json"))
    args = ap.parse_args()

    key = None
    if not args.dry_run:
        key = os.environ.get("TOUR_API_KEY") or getpass.getpass("공공데이터포털 인증키 (입력 내용은 표시되지 않음): ").strip()
        if not key:
            sys.exit("인증키가 없습니다.")

    api = Api(key, args.dry_run)
    res = collect(api, use_detail=not args.no_detail, use_odii=not args.no_odii)

    if args.dry_run:
        print(f"\n[dry-run] 목록/검색/오디 호출 예상: {api.calls}회 (캐시 {api.cache_hits}회)")
        print("  + 상세 호출: 관광지 수 × 2회 (실행 시 확정). 개발계정 일일 한도(보통 API별 1,000회)를 확인하세요.")
        return

    out = build_output(res)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    n_odii = sum(1 for p in out["places"] if p["odiiStories"])
    print(f"\n완료: {args.out}")
    print(f"  관광지 {len(out['places'])}곳 (프로토타입 장소 {sum(p['fromPrototype'] for p in out['places'])}곳, 오디 이야기 연결 {n_odii}곳)")
    print(f"  API 호출 {api.calls}회, 캐시 사용 {api.cache_hits}회")


if __name__ == "__main__":
    main()

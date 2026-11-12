package com.roadfm.car

import ai.pleos.playground.navi.constants.WaypointIndex
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.roadfm.car.navi.NaviProbe
import com.roadfm.car.ui.theme.RoadFmColors
import com.roadfm.car.ui.theme.RoadFmTheme

class MainActivity : ComponentActivity() {

    private lateinit var navi: NaviProbe

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        navi = NaviProbe(this).also { it.start() }
        setContent { RoadFmTheme { NaviTestScreen(navi) } }
    }

    override fun onDestroy() {
        navi.stop()
        super.onDestroy()
    }
}

/** 개발용: 현대차 내비(NaviHelper) 연동 확인 화면. 실제 서비스 화면 아님. */
@Composable
private fun NaviTestScreen(navi: NaviProbe) {
    val dest = navi.destination.value
    val wps = navi.waypoints.value
    Row(
        Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).padding(24.dp),
        horizontalArrangement = Arrangement.spacedBy(24.dp),
    ) {
        Column(Modifier.weight(1f).fillMaxHeight(), verticalArrangement = Arrangement.spacedBy(14.dp)) {
            Text("ROADFM · 내비 연동 테스트 (개발용)", style = MaterialTheme.typography.titleLarge)
            Text(
                when (navi.connection.value) {
                    NaviProbe.Connection.CONNECTING -> "NaviHelper 연결 중…"
                    NaviProbe.Connection.CONNECTED -> "NaviHelper 연결됨"
                    NaviProbe.Connection.FAILED -> "NaviHelper 연결 실패 — 로그 확인"
                },
                color = if (navi.connection.value == NaviProbe.Connection.FAILED) RoadFmColors.Warn else RoadFmColors.Gold,
            )
            Panel("내비 목적지 (getDestinationInfo)") {
                if (dest == null) {
                    Text("아직 받은 목적지 없음", color = RoadFmColors.Muted)
                } else {
                    Text(dest.name, style = MaterialTheme.typography.headlineMedium)
                    Text(dest.address, color = RoadFmColors.Muted)
                    Text("위도 ${dest.latitude} · 경도 ${dest.longitude}", color = RoadFmColors.Muted)
                    Text("남은 거리 ${dest.remainDistance} · 남은 시간 ${dest.remainTime}", color = RoadFmColors.Muted)
                }
            }
            Panel("내비 경유지 (getWaypointInfo) · ${wps.size}/2") {
                if (wps.isEmpty()) Text("경유지 없음", color = RoadFmColors.Muted)
                wps.forEachIndexed { i, w -> Text("${i + 1}. ${w.name} — ${w.address}") }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Button(onClick = navi::requestDestination) { Text("목적지 조회") }
                Button(onClick = navi::requestWaypoints) { Text("경유지 조회") }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                OutlinedButton(onClick = { navi.addSampleWaypoint(WaypointIndex.FIRST) }) { Text("예시 경유지 FIRST") }
                OutlinedButton(onClick = { navi.addSampleWaypoint(WaypointIndex.SECOND) }) { Text("예시 경유지 SECOND") }
                OutlinedButton(onClick = navi::removeAllWaypoints) { Text("경유지 모두 제거") }
            }
            Text(
                "확인 순서: ① 에뮬레이터 내비에서 직접 목적지 설정 → 이 화면에 오는지 ② 이 앱을 켠 채 내비 목적지 변경 → onDestinationChanged 로그 ③ 경유지 추가 시 내비 반응",
                style = MaterialTheme.typography.bodyMedium,
                color = RoadFmColors.Muted,
            )
        }
        Column(Modifier.weight(1f).fillMaxHeight()) {
            Text("이벤트 로그 (logcat 태그: ${NaviProbe.TAG})", style = MaterialTheme.typography.titleMedium)
            Spacer(Modifier.height(8.dp))
            LazyColumn(
                Modifier.fillMaxSize().background(RoadFmColors.Surface, RoundedCornerShape(12.dp)).padding(12.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                items(navi.logs) { line ->
                    Text(line, fontFamily = FontFamily.Monospace, fontSize = 13.sp, lineHeight = 18.sp)
                }
            }
        }
    }
}

@Composable
private fun Panel(title: String, content: @Composable () -> Unit) {
    Column(
        Modifier.fillMaxWidth().background(RoadFmColors.Surface, RoundedCornerShape(12.dp)).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text(title, style = MaterialTheme.typography.labelMedium, color = RoadFmColors.Muted)
        content()
    }
}

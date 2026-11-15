package com.roadfm.car.navi

import ai.pleos.playground.navi.constants.NaviErrorCode
import ai.pleos.playground.navi.constants.NavigationStatus
import ai.pleos.playground.navi.constants.WaypointIndex
import ai.pleos.playground.navi.data.DestinationInfo
import ai.pleos.playground.navi.data.RequestWaypointInfo
import ai.pleos.playground.navi.data.RouteStartInfo
import ai.pleos.playground.navi.data.WaypointChangedInfo
import ai.pleos.playground.navi.data.WaypointInfo
import ai.pleos.playground.navi.helper.NaviHelper
import ai.pleos.playground.navi.helper.listener.NaviHelperEventListener
import android.content.Context
import android.os.Handler
import android.os.Looper
import android.util.Log
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * 에뮬레이터 확인용 NaviHelper 연동 (개발용).
 *
 * 확인하려는 것:
 *  1. 사용자가 현대차 내비에서 직접 넣은 목적지를 getDestinationInfo()/onDestinationChanged()로 받을 수 있는지
 *  2. DestinationInfo 에 실제로 어떤 값이 들어오는지
 *  3. addWaypoint() 시 내비 동작(재탐색·팝업)과 경유지 3개째 요청 시 결과
 *
 * 시그니처 근거: NaviHelper 3.0.5 / navi-data 3.0.4 AAR 의 공개 API (javap 확인) + Pleos NaviHelper 가이드.
 * 모든 결과는 logcat 태그 [TAG] 와 화면 로그에 남긴다.
 */
class NaviProbe(context: Context) {

    enum class Connection { CONNECTING, CONNECTED, FAILED }

    val connection = mutableStateOf(Connection.CONNECTING)
    val destination = mutableStateOf<DestinationInfo?>(null)
    val waypoints = mutableStateOf<List<WaypointInfo>>(emptyList())
    val logs = mutableStateListOf<String>()

    private val naviHelper = NaviHelper(context.applicationContext)
    private val main = Handler(Looper.getMainLooper())
    private val timeFmt = SimpleDateFormat("HH:mm:ss", Locale.KOREA)

    /** 콜백은 SDK 쪽 스레드에서 올 수 있으므로 상태 변경은 메인 스레드에서 한다. */
    private fun ui(block: () -> Unit) = main.post(block)

    private fun log(msg: String) {
        Log.d(TAG, msg)
        ui {
            logs.add(0, "${timeFmt.format(Date())}  $msg")
            if (logs.size > MAX_LOGS) logs.removeAt(logs.lastIndex)
        }
    }

    private val listener = object : NaviHelperEventListener {
        override fun onDestinationInfo(destinationInfo: DestinationInfo) {
            log("onDestinationInfo: $destinationInfo")
            val valid = destinationInfo.takeUnless { it.isEmpty() }
            ui { destination.value = valid }
        }

        override fun onDestinationChanged() {
            log("onDestinationChanged → 목적지 다시 조회")
            naviHelper.getDestinationInfo()
        }

        override fun onWayPointInfo(waypointInfoList: List<WaypointInfo>) {
            log("onWayPointInfo (${waypointInfoList.size}개): $waypointInfoList")
            ui { waypoints.value = waypointInfoList }
        }

        override fun onWaypointChanged(waypointChangedInfo: WaypointChangedInfo) {
            log("onWaypointChanged: $waypointChangedInfo → 경유지 다시 조회")
            naviHelper.getWaypointInfo()
        }

        override fun onRouteStarted(routeStartInfo: RouteStartInfo) = log("onRouteStarted: $routeStartInfo")
        override fun onRoutingCompleted() = log("onRoutingCompleted")
        override fun onReRouteEnded() = log("onReRouteEnded")
        override fun onRouteCancelled() = log("onRouteCancelled")
        override fun onRouteEnded() = log("onRouteEnded")
        override fun onNavigationStatus(navigationStatus: NavigationStatus) {
            log("onNavigationStatus: $navigationStatus")
            if (navigationStatus == NavigationStatus.ROUTE_DRIVE) {
                log("길 안내 재시작 → 목적지 다시 조회")
                naviHelper.getDestinationInfo()
            }
        }
        override fun onError(errorCode: NaviErrorCode) = log("onError: $errorCode")
    }

    fun start() {
        log("NaviHelper 초기화 시작")
        naviHelper.initialize(
            {
                log("연결 성공 → 리스너 등록, 목적지·경유지 조회")
                ui { connection.value = Connection.CONNECTED }
                naviHelper.addListener(listener)
                naviHelper.getDestinationInfo()
                naviHelper.getWaypointInfo()
            },
            { throwable ->
                Log.e(TAG, "연결 실패", throwable)
                log("연결 실패: ${throwable.message}")
                ui { connection.value = Connection.FAILED }
            },
        )
    }

    fun requestDestination() { log("getDestinationInfo() 호출"); naviHelper.getDestinationInfo() }

    fun requestWaypoints() { log("getWaypointInfo() 호출"); naviHelper.getWaypointInfo() }

    /** Pleos 경유지 가이드의 예시 장소로 경유지 추가를 요청한다(테스트용 고정값). */
    fun addSampleWaypoint(index: WaypointIndex) {
        log("addWaypoint($index) 호출 — 가이드 예시 장소")
        naviHelper.addWaypoint(
            RequestWaypointInfo(
                latitude = 37.41275833,
                longitude = 127.09481944,
                poiName = "소프트웨어드림센터",
                waypointIndex = index,
                poiId = "36khp2hdj2cfcm5nqhe3",
                address = "경기도 성남시 수정구 창업로40번길 6",
                poiSubId = "0",
            ),
        )
    }

    fun removeAllWaypoints() { log("removeWaypoint(ALL) 호출"); naviHelper.removeWaypoint(WaypointIndex.ALL) }

    fun stop() {
        naviHelper.removeListener(listener)
        naviHelper.release()
        main.removeCallbacksAndMessages(null)
    }

    private fun DestinationInfo.isEmpty() = name.isBlank() && latitude == 0.0 && longitude == 0.0

    companion object {
        const val TAG = "RoadFmNavi"
        private const val MAX_LOGS = 80
    }
}

package com.roadfm.car.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

/** 다크 그린 · 차콜 · 아이보리 + 절제된 골드 강조. 차량 화면 가독성 우선(큰 글자, 높은 대비). */
object RoadFmColors {
    val Background = Color(0xFF121614)
    val Surface = Color(0xFF1A201D)
    val SurfaceHigh = Color(0xFF232B27)
    val Green = Color(0xFF1F3A2E)
    val GreenLight = Color(0xFF3E6B55)
    val Ivory = Color(0xFFF2EDE3)
    val Muted = Color(0xFF9AA59F)
    val Gold = Color(0xFFC9A86A)
    val Warn = Color(0xFFD9895B)
}

private val colors = darkColorScheme(
    primary = RoadFmColors.Gold,
    onPrimary = RoadFmColors.Background,
    secondary = RoadFmColors.GreenLight,
    onSecondary = RoadFmColors.Ivory,
    background = RoadFmColors.Background,
    onBackground = RoadFmColors.Ivory,
    surface = RoadFmColors.Surface,
    onSurface = RoadFmColors.Ivory,
    surfaceVariant = RoadFmColors.SurfaceHigh,
    onSurfaceVariant = RoadFmColors.Muted,
    error = RoadFmColors.Warn,
)

private val typography = Typography(
    displaySmall = TextStyle(fontSize = 40.sp, fontWeight = FontWeight.Light, letterSpacing = (-0.5).sp),
    headlineMedium = TextStyle(fontSize = 30.sp, fontWeight = FontWeight.Normal),
    titleLarge = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.Medium),
    titleMedium = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Medium),
    bodyLarge = TextStyle(fontSize = 19.sp, lineHeight = 28.sp),
    bodyMedium = TextStyle(fontSize = 17.sp, lineHeight = 25.sp),
    labelLarge = TextStyle(fontSize = 17.sp, fontWeight = FontWeight.Medium),
    labelMedium = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium, letterSpacing = 1.5.sp),
)

@Composable
fun RoadFmTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = colors, typography = typography, content = content)
}

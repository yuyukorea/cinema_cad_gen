import io
import ezdxf
from ezdxf import colors

def generate_cinema_dxf(room_w, room_l, room_h, screen_w, spk_main, spk_sub, spk_surr, proj_model):
    """상영관 수치와 장비 스펙을 받아 DXF 바이너리 스트림을 반환합니다."""
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # 1. 레이어 정의
    layers = [
        ("WALLS", colors.WHITE),
        ("SCREEN", colors.CYAN),
        ("SEATS", colors.GRAY),
        ("SPEAKERS_MAIN", colors.RED),
        ("SPEAKERS_SUB", colors.MAGENTA),
        ("SPEAKERS_SURROUND", colors.GREEN),
        ("DIMENSIONS", colors.YELLOW),
        ("TEXT", colors.WHITE)
    ]
    for name, col in layers:
        doc.layers.add(name=name, color=col)

    half_w = room_w / 2.0

    # 2. 상영관 외벽
    msp.add_lwpolyline(
        [(-half_w, 0), (half_w, 0), (half_w, room_l), (-half_w, room_l), (-half_w, 0)],
        dxfattribs={'layer': 'WALLS'}
    )

    # 3. 스크린 (Screen)
    scr_half = screen_w / 2.0
    msp.add_line((-scr_half, 1.2), (scr_half, 1.2), dxfattribs={'layer': 'SCREEN'})
    msp.add_text(f"SCREEN: {screen_w}m", dxfattribs={'layer': 'SCREEN', 'height': 0.35}).set_placement(( -1.5, 1.4))

    # 4. 전방 메인 스피커 (L, C, R)
    # L/R은 스크린 좌우 엣지 안쪽, C는 중앙
    for x_pos, tag in [(-scr_half * 0.9, f"L: {spk_main}"), (0.0, f"C: {spk_main}"), (scr_half * 0.9, f"R: {spk_main}")]:
        msp.add_lwpolyline([
            (x_pos - 0.4, 0.2), (x_pos + 0.4, 0.2), 
            (x_pos + 0.4, 0.8), (x_pos - 0.4, 0.8), (x_pos - 0.4, 0.2)
        ], dxfattribs={'layer': 'SPEAKERS_MAIN'})
        msp.add_text(tag, dxfattribs={'layer': 'SPEAKERS_MAIN', 'height': 0.2, 'rotation': 90}).set_placement((x_pos - 0.1, 0.3))

    # 5. 서브우퍼 (LFE 2대 기본 배치)
    for x_pos in [-half_w * 0.25, half_w * 0.25]:
        msp.add_lwpolyline([
            (x_pos - 0.5, 0.2), (x_pos + 0.5, 0.2), 
            (x_pos + 0.5, 0.9), (x_pos - 0.5, 0.9), (x_pos - 0.5, 0.2)
        ], dxfattribs={'layer': 'SPEAKERS_SUB'})
        msp.add_text(f"SUB: {spk_sub}", dxfattribs={'layer': 'SPEAKERS_SUB', 'height': 0.18}).set_placement((x_pos - 0.4, 0.4))

    # 6. 서라운드 스피커 (상영관 길이에 따른 등간격 자동 배치)
    # 5m 지점부터 후방 1m 전까지 2.2m~2.5m 피치로 배치
    y_start = 5.0
    y_end = room_l - 1.0
    pitch = 2.4
    surr_count = max(3, int((y_end - y_start) / pitch))
    actual_pitch = (y_end - y_start) / surr_count

    for i in range(surr_count + 1):
        y_pos = y_start + (i * actual_pitch)
        # 좌측벽
        msp.add_lwpolyline([(-half_w, y_pos - 0.2), (-half_w + 0.3, y_pos - 0.2), (-half_w + 0.3, y_pos + 0.2), (-half_w, y_pos + 0.2), (-half_w, y_pos - 0.2)], dxfattribs={'layer': 'SPEAKERS_SURROUND'})
        # 우측벽
        msp.add_lwpolyline([(half_w, y_pos - 0.2), (half_w - 0.3, y_pos - 0.2), (half_w - 0.3, y_pos + 0.2), (half_w, y_pos + 0.2), (half_w, y_pos - 0.2)], dxfattribs={'layer': 'SPEAKERS_SURROUND'})

    # 7. 프로젝터 표기 (후방 영사실 중앙)
    msp.add_lwpolyline([(-0.6, room_l - 0.8), (0.6, room_l - 0.8), (0.6, room_l), (-0.6, room_l), (-0.6, room_l - 0.8)], dxfattribs={'layer': 'DIMENSIONS'})
    msp.add_text(f"PROJ: {proj_model}", dxfattribs={'layer': 'TEXT', 'height': 0.25}).set_placement((-1.5, room_l - 1.2))

    # 8. 기준 청취점(RLP: 2/3 지점)
    rlp_y = room_l * (2.0 / 3.0)
    msp.add_line((-0.5, rlp_y), (0.5, rlp_y), dxfattribs={'layer': 'DIMENSIONS'})
    msp.add_line((0, rlp_y - 0.5), (0, rlp_y + 0.5), dxfattribs={'layer': 'DIMENSIONS'})
    msp.add_text(f"RLP (Y={rlp_y:.1f}m)", dxfattribs={'layer': 'DIMENSIONS', 'height': 0.25}).set_placement((0.6, rlp_y))

    # DXF 바이트 스트림 변환
    out_stream = io.StringIO()
    doc.write(out_stream)
    return out_stream.getvalue().encode('utf-8')

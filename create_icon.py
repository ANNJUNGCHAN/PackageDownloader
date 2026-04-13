"""아이콘 생성 스크립트"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # 아이콘 크기들 (Windows ICO 표준)
    sizes = [16, 32, 48, 64, 128, 256]

    images = []

    for size in sizes:
        # 새 이미지 생성 (RGBA)
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 배경 원 (그라데이션 효과를 위해 여러 원)
        center = size // 2
        radius = size // 2 - 2

        # 메인 배경 (파란색 그라데이션 느낌)
        draw.ellipse(
            [center - radius, center - radius, center + radius, center + radius],
            fill='#2196F3'  # Material Blue
        )

        # 내부 하이라이트
        highlight_radius = radius - size // 8
        draw.ellipse(
            [center - highlight_radius, center - highlight_radius - size//16,
             center + highlight_radius, center + highlight_radius - size//16],
            fill='#42A5F5'  # Lighter blue
        )

        # 다운로드 화살표 그리기
        arrow_color = 'white'
        line_width = max(1, size // 16)

        # 화살표 몸통 (세로선)
        arrow_top = center - size // 4
        arrow_bottom = center + size // 6
        draw.line(
            [(center, arrow_top), (center, arrow_bottom)],
            fill=arrow_color, width=line_width
        )

        # 화살표 머리 (V자)
        arrow_head_size = size // 5
        draw.line(
            [(center - arrow_head_size, arrow_bottom - arrow_head_size),
             (center, arrow_bottom)],
            fill=arrow_color, width=line_width
        )
        draw.line(
            [(center + arrow_head_size, arrow_bottom - arrow_head_size),
             (center, arrow_bottom)],
            fill=arrow_color, width=line_width
        )

        # 밑줄 (트레이/베이스)
        base_y = center + size // 4
        base_width = size // 3
        draw.line(
            [(center - base_width, base_y), (center + base_width, base_y)],
            fill=arrow_color, width=line_width
        )

        # 박스 모서리 (패키지 느낌)
        corner_size = size // 6
        # 왼쪽 위 모서리
        draw.line(
            [(center - base_width, base_y), (center - base_width, base_y - corner_size)],
            fill=arrow_color, width=line_width
        )
        # 오른쪽 위 모서리
        draw.line(
            [(center + base_width, base_y), (center + base_width, base_y - corner_size)],
            fill=arrow_color, width=line_width
        )

        images.append(img)

    # ICO 파일로 저장
    icon_path = os.path.join(os.path.dirname(__file__), 'pkgdown.ico')
    images[0].save(
        icon_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )

    print(f"아이콘 생성 완료: {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_icon()

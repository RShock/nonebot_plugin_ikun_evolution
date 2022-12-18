import asyncio
import base64
import random
import re
from io import BytesIO
from math import ceil
from pathlib import Path
from typing import List, Literal, Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFile, ImageFilter, ImageFont
from nonebot import logger

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None


class BuildImage:
    """
    快捷生成图片与操作图片的工具类
    """

    def __init__(
        self,
        w: int,
        h: int,
        paste_image_width: int = 0,
        paste_image_height: int = 0,
        color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]] = None,
        image_mode: str = "RGBA",
        font_size: int = 10,
        background: Union[Optional[str], BytesIO, Path] = None,
        font: str = "yz.ttf",
        ratio: float = 1,
        is_alpha: bool = False,
        plain_text: Optional[str] = None,
        font_color: Optional[Union[str, Tuple[int, int, int]]] = None,
    ):
        """
        参数:
            :param w: 自定义图片的宽度，w=0时为图片原本宽度
            :param h: 自定义图片的高度，h=0时为图片原本高度
            :param paste_image_width: 当图片做为背景图时，设置贴图的宽度，用于贴图自动换行
            :param paste_image_height: 当图片做为背景图时，设置贴图的高度，用于贴图自动换行
            :param color: 生成图片的颜色
            :param image_mode: 图片的类型
            :param font_size: 文字大小
            :param background: 打开图片的路径
            :param font: 字体，默认在 resource/ttf/ 路径下
            :param ratio: 倍率压缩
            :param is_alpha: 是否背景透明
            :param plain_text: 纯文字文本
        """
        self.w = int(w)
        self.h = int(h)
        self.paste_image_width = int(paste_image_width)
        self.paste_image_height = int(paste_image_height)
        self._current_w = 0
        self._current_h = 0
        self.font = ImageFont.truetype(str(FONT_PATH / font), int(font_size))
        if not plain_text and not color:
            color = (255, 255, 255)
        self.background = background
        if not background:
            if plain_text:
                if not color:
                    color = (255, 255, 255, 0)
                ttf_w, ttf_h = self.getsize(plain_text)
                self.w = self.w if self.w > ttf_w else ttf_w
                self.h = self.h if self.h > ttf_h else ttf_h
            self.markImg = Image.new(image_mode, (self.w, self.h), color)
            self.markImg.convert(image_mode)
        else:
            if not w and not h:
                self.markImg = Image.open(background)
                w, h = self.markImg.size
                if ratio and ratio > 0 and ratio != 1:
                    self.w = int(ratio * w)
                    self.h = int(ratio * h)
                    self.markImg = self.markImg.resize(
                        (self.w, self.h), Image.ANTIALIAS
                    )
                else:
                    self.w = w
                    self.h = h
            else:
                self.markImg = Image.open(background).resize(
                    (self.w, self.h), Image.ANTIALIAS
                )
        if is_alpha:
            try:
                array = self.markImg.load()
                for i in range(w):
                    for j in range(h):
                        pos = array[i, j]
                        is_edit = sum([1 for x in pos[0:3] if x > 240]) == 3
                        if is_edit:
                            array[i, j] = (255, 255, 255, 0)
            except Exception as e:
                logger.warning(f"背景透明化发生错误..{type(e)}：{e}")
        self.draw = ImageDraw.Draw(self.markImg)
        self.size = self.w, self.h
        if plain_text:
            fill = font_color if font_color else (0, 0, 0)
            self.text((0, 0), plain_text, fill)
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            self.loop = asyncio.get_event_loop()


async def text2image(
    text: str,
    auto_parse: bool = True,
    font_size: int = 20,
    color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]] = "white",
    font: str = "CJGaoDeGuo.otf",
    font_color: Union[str, Tuple[int, int, int]] = "black",
    padding: Union[int, Tuple[int, int, int, int]] = 0,
    _add_height: float = 0,
) -> BuildImage:
    """
    说明:
        解析文本并转为图片
        使用标签
            <f> </f>
        可选配置项
            font: str -> 特殊文本字体
            fs / font_size: int -> 特殊文本大小
            fc / font_color: Union[str, Tuple[int, int, int]] -> 特殊文本颜色
        示例
            在不在，<f font=YSHaoShenTi-2.ttf font_size=30 font_color=red>HibiKi小姐</f>，
            你最近还好吗，<f font_size=15 font_color=black>我非常想你</f>，这段时间我非常不好过，
            <f font_size=25>抽卡抽不到金色</f>，这让我很痛苦
    参数:
        :param text: 文本
        :param auto_parse: 是否自动解析，否则原样发送
        :param font_size: 普通字体大小
        :param color: 背景颜色
        :param font: 普通字体
        :param font_color: 普通字体颜色
        :param padding: 文本外边距，元组类型时为 （上，左，下，右）
        :param _add_height: 由于get_size无法返回正确的高度，采用手动方式额外添加高度
    """
    pw = ph = top_padding = left_padding = 0
    if padding:
        if isinstance(padding, int):
            pw = padding * 2
            ph = padding * 2
            top_padding = left_padding = padding
        elif isinstance(padding, tuple):
            pw = padding[0] + padding[2]
            ph = padding[1] + padding[3]
            top_padding = padding[0]
            left_padding = padding[1]
    if auto_parse and re.search(r"<f(.*)>(.*)</f>", text):
        _data = []
        new_text = ""
        placeholder_index = 0
        for s in text.split("</f>"):
            r = re.search(r"<f(.*)>(.*)", s)
            if r:
                start, end = r.span()
                if start != 0 and (t := s[:start]):
                    new_text += t
                _data.append(
                    [
                        (start, end),
                        f"[placeholder_{placeholder_index}]",
                        r.group(1).strip(),
                        r.group(2),
                    ]
                )
                new_text += f"[placeholder_{placeholder_index}]"
                placeholder_index += 1
        new_text += text.split("</f>")[-1]
        image_list = []
        current_placeholder_index = 0
        # 切分换行，每行为单张图片
        for s in new_text.split("\n"):
            _tmp_text = s
            img_height = BuildImage(0, 0, font_size=font_size).getsize("正")[1]
            img_width = 0
            _tmp_index = current_placeholder_index
            for _ in range(s.count("[placeholder_")):
                placeholder = _data[_tmp_index]
                if "font_size" in placeholder[2]:
                    r = re.search(r"font_size=['\"]?(\d+)", placeholder[2])
                    if r:
                        w, h = BuildImage(0, 0, font_size=int(r.group(1))).getsize(
                            placeholder[3]
                        )
                        img_height = img_height if img_height > h else h
                        img_width += w
                else:
                    img_width += BuildImage(0, 0, font_size=font_size).getsize(
                        placeholder[3]
                    )[0]
                _tmp_text = _tmp_text.replace(f"[placeholder_{_tmp_index}]", "")
                _tmp_index += 1
            img_width += BuildImage(0, 0, font_size=font_size).getsize(_tmp_text)[0]
            # img_width += len(_tmp_text) * font_size
            # 开始画图
            A = BuildImage(
                img_width, img_height, color=color, font=font, font_size=font_size
            )
            basic_font_h = A.getsize("正")[1]
            current_width = 0
            # 遍历占位符
            for _ in range(s.count("[placeholder_")):
                if not s.startswith(f"[placeholder_{current_placeholder_index}]"):
                    slice_ = s.split(f"[placeholder_{current_placeholder_index}]")
                    await A.atext(
                        (current_width, A.h - basic_font_h - 1), slice_[0], font_color
                    )
                    current_width += A.getsize(slice_[0])[0]
                placeholder = _data[current_placeholder_index]
                # 解析配置
                _font = font
                _font_size = font_size
                _font_color = font_color
                for e in placeholder[2].split():
                    if e.startswith("font="):
                        _font = e.split("=")[-1]
                    if e.startswith("font_size=") or e.startswith("fs="):
                        _font_size = int(e.split("=")[-1])
                        if _font_size > 1000:
                            _font_size = 1000
                        if _font_size < 1:
                            _font_size = 1
                    if e.startswith("font_color") or e.startswith("fc="):
                        _font_color = e.split("=")[-1]
                text_img = BuildImage(
                    0,
                    0,
                    plain_text=placeholder[3],
                    font_size=_font_size,
                    font_color=_font_color,
                    font=_font,
                )
                _img_h = (
                    int(A.h / 2 - text_img.h / 2)
                    if new_text == "[placeholder_0]"
                    else A.h - text_img.h
                )
                await A.apaste(text_img, (current_width, _img_h - 1), True)
                current_width += text_img.w
                s = s[
                    s.index(f"[placeholder_{current_placeholder_index}]")
                    + len(f"[placeholder_{current_placeholder_index}]") :
                ]
                current_placeholder_index += 1
            if s:
                slice_ = s.split(f"[placeholder_{current_placeholder_index}]")
                await A.atext((current_width, A.h - basic_font_h), slice_[0])
                current_width += A.getsize(slice_[0])[0]
            A.crop((0, 0, current_width, A.h))
            # A.show()
            image_list.append(A)
        height = 0
        width = 0
        for img in image_list:
            height += img.h
            width = width if width > img.w else img.w
        width += pw
        height += ph
        A = BuildImage(width + left_padding, height + top_padding, color=color)
        current_height = top_padding
        for img in image_list:
            await A.apaste(img, (left_padding, current_height), True)
            current_height += img.h
    else:
        width = 0
        height = 0
        _tmp = BuildImage(0, 0, font=font, font_size=font_size)
        _, h = _tmp.getsize("正")
        line_height = int(font_size / 3)
        image_list = []
        for x in text.split("\n"):
            w, _ = _tmp.getsize(x.strip() or "正")
            height += h + line_height
            width = width if width > w else w
            image_list.append(BuildImage(w, h, font=font, font_size=font_size, plain_text=x.strip(), color=color))
        width += pw
        height += ph
        A = BuildImage(
            width + left_padding,
            height + top_padding + 2,
            color=color,
        )
        cur_h = ph
        for img in image_list:
            await A.apaste(img, (pw, cur_h), True)
            cur_h += img.h + line_height
    return A


if __name__ == "__main__":
    pass

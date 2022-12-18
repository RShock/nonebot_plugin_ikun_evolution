import io
import os
from pathlib import Path
from typing import Union

from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, GroupMessageEvent



def add_items(a, b) -> dict[str, int]:
    temp = dict()
    for key in a.keys() | b.keys():
        temp[key] = round(sum([d.get(key, 0) for d in (a, b)]), 2)
    return temp


def add_item(dic, name, cnt=1):
    if dic.get(name) is None:
        dic[name] = round(cnt)
    else:
        dic[name] = round(dic[name] + cnt, 2)


game_path = os.path.dirname(__file__)


# 不知道官方的那个image怎么用 只能直接用自己文件下的的resources+MessageSegment了 会用的可以告诉我
def get_image(type, name):
    image_file = f"file:///{game_path}/gamedata/image/{type}/{name}"
    return MessageSegment.image(image_file)


SESSION_CODE = "S1"  # 不同赛季的账号是完全不同的


def get_uid(event) -> str:
    return str(event.user_id) + SESSION_CODE


def get_act_str(name) -> str:
    return '正在' + name


async def send_group_msg(
        bot: Bot,
        event: GroupMessageEvent,
        name: str,
        msgs: list[str],
):
    """
    发送合并消息(发送人名称相同)
    @param bot: 机器人的引用
    @param event: 用来获取群id
    @param name: 发消息的人的名字
    @param msgs: 要发的消息(list[str])
    @return:
    """
    messages = [MessageSegment.node_custom(bot.self_id, name, m) for m in msgs]
    await bot.call_api(
        "send_group_forward_msg", group_id=event.group_id, messages=messages
    )


async def send_group_msg_pic(
        bot: Bot,
        name: str,
        msgs: list[str],
):
    """
    发送合并消息(发送人名称相同)的图片，风控时使用
    @param bot: 机器人的引用
    @param event: 用来获取群id
    @param name: 发消息的人的名字
    @param msgs: 要发的消息(list[str])
    @return:
    """
    msg = "\n\n".join(msgs)
    result = f"{name}:\n{msg}"
    await send_img(bot, result)


async def send_group_msg_pic2(
        bot: Bot,
        msgs: list[tuple],
):
    """
    发送合并消息(发送人名称不同)的图片，风控时使用
    @param bot: 机器人的引用
    @param event: 用来获取群id
    @param msgs: 要发的消息([list[(str,str)]）e.g.[("真寻","我爱你"),...]
    @return:
    """
    tmp = io.StringIO()
    tmp2 = ""
    for name, msg in msgs:
        if name != tmp2:
            tmp2 = name
            tmp.write(name)
            tmp.write(':\n')
        tmp.write(msg)
        tmp.write('\n')
    await send_img(bot, tmp.getvalue())


# text2image是真寻独有的方法 nonebot显示不了:(
async def send_img(bot, msg: str):
    return


async def send_group_msg2(
        bot: Bot,
        event: GroupMessageEvent,
        msgs: list[tuple],
):
    """
    发送合并消息(发送人名称不同)
    @param bot: 机器人的引用
    @param event: 用来获取群id
    @param msgs: 要发的消息([list[(str,str)]）e.g.[("真寻","我爱你"),...]
    @return:
    """
    messages = [MessageSegment.node_custom(bot.self_id, m[0], m[1]) for m in msgs]
    await bot.call_api(
        "send_group_forward_msg", group_id=event.group_id, messages=messages
    )


def fill_list(my_list: list, length, fill=None):  # 使用 fill字符/数字 填充，使得最后的长度为 length
    if len(my_list) >= length:
        return my_list
    else:
        return my_list + (length - len(my_list)) * [fill]


def image(
        file: Union[str, Path, bytes] = None,
        path: str = None,
        b64: str = None,
) -> Union[MessageSegment, str]:
    """
    说明:
        生成一个 MessageSegment.image 消息
        生成顺序：绝对路径(abspath) > base64(b64) > img_name
    参数:
        :param file: 图片文件名称，默认在 resource/img 目录下
        :param path: 图片所在路径，默认在 resource/img 目录下
        :param b64: 图片base64
    """
    if isinstance(file, Path):
        if file.exists():
            return MessageSegment.image(file)
        logger.warning(f"图片 {file.absolute()}缺失...")
        return ""
    elif isinstance(file, (bytes, io.BytesIO)):
        return MessageSegment.image(file)
    elif b64:
        return MessageSegment.image(b64 if "base64://" in b64 else "base64://" + b64)
    else:
        if file.startswith("http"):
            return MessageSegment.image(file)
        if len(file.split(".")) == 1:
            file += ".jpg"
        else:
            logger.warning(f"图片 {file} 缺失...")
            return ""

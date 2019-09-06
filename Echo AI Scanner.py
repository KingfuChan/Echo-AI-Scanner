import os
import chardet
import configparser

copyright = """FSX/Prepar3D AI机模扫描器 for ECHO
作者：CDorJF/SINO6749
网站：https://bbs.sinofsx.com/forum.php?mod=viewthread&tid=187056
不得用作商业用途
"""


class OutputXml(object):

    def __init__(self):
        self.text = ""
        self.count = 0

    def add_entry(self, entry):
        t = f"""    <Airplane AtcModel="{entry['AtcModel']}" Title="{entry['Title']}" Airline="{entry['Airline']}" />\n"""
        self.text += t
        self.count += 1

    def save(self, filename):
        with open(filename, 'w', encoding='utf-8') as o:
            o.write("<AirplaneModels>\n")
            o.write(self.text)
            o.write("</AirplaneModels>")


def get_cfg_list(directory):
    print("读取全部Aircraft.cfg文件...")
    cfglist = []
    for root, _dirname, filelist in os.walk(directory):
        for f in filelist:
            if str(f).lower() == 'aircraft.cfg':
                cfglist.append(f"{root}\\{f}")
    print(f"读取到{len(cfglist)}个Aircraft.cfg文件")
    return cfglist


def parse_cfg(cfg_file_path):

    parser = configparser.ConfigParser(
        comment_prefixes=('#', ';', '//'), inline_comment_prefixes='//', strict=False, allow_no_value=True)
    print(f"正在处理{cfg_file_path}...")
    with open(cfg_file_path, 'rb',) as f:
        r = f.read()
        encode = chardet.detect(r)['encoding']

    try:
        parser.read_string(r.decode(encode))
    except configparser.Error as e:
        print("发生错误", e)
        return []

    sect = parser.sections()

    generalsect = [s for s in sect if str(s).lower() == 'general']
    try:
        model = [parser[gs]['atc_model'] for gs in generalsect]
    except KeyError:
        print(f"{cfg_file_path}内容有错误，跳过...")
        return []
    model = model[0]
    fltsim = [s for s in sect if 'fltsim' in str(s).lower()]
    entries = []
    for fs in fltsim:
        content = parser[fs]
        title = content['title']
        if '"' in title or '&' in title or '>' in title or '<' in title or "'" in title:
            continue  # 避免导出的XML格式有误

        try:  # 判断是否有此项
            callsign = content['atc_parking_codes']
        except KeyError:
            callsign = ''

        if callsign:  # callsign处理，消除重复，补充缺漏
            callsign = str(callsign).rsplit(',')[0]
        else:
            try:
                callsign = str(title).rsplit('.')[1]
            except IndexError:
                callsign = ''

        entries.append(
            {'AtcModel': model, 'Title': title, 'Airline': callsign})

    return entries


def scan_ai_models():
    diript = input("请输入所需扫描的AI机模目录：\n>>>")
    SimObjectDir = os.path.abspath(diript)
    if not (os.path.exists(SimObjectDir) and diript):
        print("请检查输入的文件夹路径！\n")
        return scan_ai_models()

    entries = []
    for cl in get_cfg_list(SimObjectDir):
        entries.extend(parse_cfg(cl))
    output = OutputXml()
    for e in entries:
        output.add_entry(e)
    savename = os.path.join(
        os.environ['userprofile'], 'AppData\Local\Hans_Creation\ECHO Pilot Client\Rules\Echo AI Scanner.xml')
    output.save(savename)
    print(f"成功生成{output.count}条匹配规则！")
    print("匹配规则已生成到Echo匹配规则文件夹，请直接在在客户端中选择Echo AI Scanner。")
    _end = input("按回车键退出...")


def create_hard_link():
    oriipt = input("请输入AI机模所在文件夹：\n>>>")
    dstipt = input("请输入SimObjects\\Airplanes文件夹：\n>>>")
    ori = os.path.abspath(oriipt)
    dst = os.path.abspath(dstipt)
    if not (ori != dst and os.path.exists(ori) and oriipt and dstipt):
        print("请检查输入的文件夹路径！\n")
        return create_hard_link()

    newname = f"{os.path.basename(ori)}_Linked"
    ren = os.path.join(os.path.dirname(ori), newname)
    os.rename(ori, ren)
    print(f"为避免模拟器加载时出错，已将AI机模文件夹重命名为{newname}。")
    _pause = input("按回车键开始创建目录联接...")

    counter = 0
    for d in os.listdir(ren):
        source = os.path.join(ren, d)
        destination = os.path.join(dst, d)
        os.system(f'mklink /j "{destination}" "{source}"')
        counter += 1

    input(f"已创建{counter}个目录联接！\n按回车键退出...")


if __name__ == "__main__":
    print(copyright)
    mode = input("扫描机模\t----输入 1\n创建目录联接\t----输入 2\n>>>")
    if mode == '1':
        scan_ai_models()
    elif mode == '2':
        create_hard_link()

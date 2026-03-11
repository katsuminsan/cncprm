import re
import json
from pathlib import Path
from ..model.parameter_set import ParameterSet
from ..core.Types import AxisType, ValueType, FormatType

# 軸・値ペアを抽出する正規表現
pattern_Nnum = re.compile(r"([N])(\d+)")
pattern_QindexAxOrValue = re.compile(r"([Q])(\d+)([A|S|T|L|P|M|I]\d+.+)")
pattern_AxValue = re.compile(r"([A|S|T|L])(\d+)([P|M|I])([\d\.\-]+)")
pattern_OnlyValue = re.compile(r"([P|M|I])([\d\.\-]+)")
ZEN2HAN = str.maketrans(''.join(chr(0xff01 + i) for i in range(94)), ''.join(chr(0x21 + i) for i in range(94)))

class CncprmParser():
    def __init__(self, path=None):
        if isinstance(path, str):
            path = Path(path)
        self.__initialize_model()
        if path is not None:
            self.load(path)

    def __len__(self):
        """パラメータの総数を返す"""
        return len(self.fullbody["data"])
    
    def __initialize_model(self):
        self.fullbody = {"data":[], "index":{}}

    def loads(self, text, separater=r"\n"):
        """cncprm形式の文字列からCncprmModelを返す"""
        self.__initialize_model()

        lines = separater.split(text)
        for line in lines:
            line = str(line).upper().translate(ZEN2HAN)
            x = self.parse(line)
            if x is None:
                continue
            self.fullbody["data"].append(x[0])
            self.fullbody["index"].update(x[1])
        return self.fullbody
    
        return b
    def load(self, path):
        """cncprm形式のテキスト形式のファイルパスからCncprmModelを返す"""
        # 入力ファイルを読み込み
        # 読み込まれた文字はは半角、大文字へ自動置換される。
        self.__initialize_model()
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        for line in lines:
            line = str(line).upper().translate(ZEN2HAN)
            x = self.parse(line)
            if x is None:
                continue
            self.fullbody["data"].append(x[0])
            self.fullbody["index"].update(x[1])
        return self.fullbody

    def parse(self, prm_line):
        prm_line = prm_line.strip()

        # N番号を抽出
        if not pattern_Nnum.search(prm_line):
            return None
        parts = pattern_Nnum.search(prm_line)

        if parts:
            N_letter, N_index = parts.groups()
            N_number = {"N_letter": N_letter, "N_index": int(N_index)}
        
            Ndata_part = pattern_Nnum.sub("", prm_line)
        if Ndata_part:
            if not pattern_QindexAxOrValue.search(Ndata_part):
                return None
            for match in pattern_QindexAxOrValue.finditer(Ndata_part):
                Q_letter, Q_index, Q_data_part = match.groups()
                Q_number = {"Q_letter": Q_letter, "Q_index": int(Q_index)}
                _d = self.__extract_axis_values(Q_data_part)
                if _d is not None:
                    _d.update(
                        {
                            "N_number": N_number,
                            "Q_number": Q_number,
                            "raw_line": prm_line
                        }
                    )
                    return _d, {_d["N_number"]["N_index"]: _d}
            
    def __extract_axis_values(self, data_part):
        axis_values = []
        axis_letter, axis_index, value_letter, value = ('', 0, '', '')
        if pattern_AxValue.search(data_part):
            # 軸と値のペアを抽出
            for match in pattern_AxValue.finditer(data_part):
                axis_letter, axis_index, value_letter, value = match.groups()
                axis_values.append(
                    {"axis_letter": f"{axis_letter}", "axis_index": int(axis_index),
                    "value_letter": value_letter, "value": f"{value}"}
                )
                axis_type = getattr(AxisType, axis_letter, AxisType.NONE)
                value_type = getattr(ValueType, value_letter, ValueType.P)
        elif pattern_OnlyValue.search(data_part):
            matchValues = pattern_OnlyValue.findall(data_part)[0]
            value_letter, value = matchValues[0], matchValues[1]
            axis_values.append(
                {"axis_letter": axis_letter, "axis_index": int(axis_index),
                "value_letter": value_letter,"value": f"{value}"}
            )
            axis_type = AxisType.NONE
            value_type = getattr(ValueType, value_letter, ValueType.P)
        else:
            raise ValueError(f"errValue: {data_part}")

        # 軸インデックス順にソート
        axis_values.sort(key=lambda x: x["axis_index"] if x["axis_index"] != '' else 0)

        # format判定
        values_only = [v["value"] for v in axis_values]
        if all(len(v) == 8 and set(v) <= {"0", "1"} for v in values_only):
            fmt = FormatType.BIT_8
        elif any("." in v for v in values_only):
            fmt = FormatType.DECIMAL
        else:
            fmt = FormatType.INTEGER

        return ParameterSet(
            no=axis_index,
            axis_type=axis_type,
            value_type=value_type,
            fmt=fmt,
            raw_line=data_part
        )
        
    def export_parameterByJson(self, path = "parameter.josn"):
        # JSONファイルに保存
        if not self.fullbody["data"]:
            return None
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                self.fullbody["data"], 
                f, 
                ensure_ascii=False, 
                indent=4
            )

    def export_typeindexByJson(self, path = "typeindex.json"):
        # 各N番号ごとのタイプだけを N番号をキーとした辞書へ出力する。
        if not self.fullbody["data"]:
            return None
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {d["N_number"]["N_index"]:d["types"] for d in self.fullbody["data"]}, 
                f, 
                ensure_ascii=False, 
                indent=4
            )
        
if __name__ == '__main__':
    filepath = Path("src/data/CNC-PARA.TXT")
    print(filepath.resolve())
    p = CncprmParser(filepath)
    p.export_parameterByJson("outputs/parameter.json")
    p.export_typeindexByJson("outputs/typeindex.json")

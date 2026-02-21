import re
import json
from pathlib import Path

# 軸・値ペアを抽出する正規表現
pattern_Nnum = re.compile(r"([N])(\d+)")
pattern_QindexAxOrValue = re.compile(r"([Q])(\d+)([A|S|T|L|P|M|I]?\d+)")
pattern_AxValue = re.compile(r"([A|S|T|L])(\d+)([P|M|I])([\d\.\-]+)")
pattern_OnlyValue = re.compile(r"([P|M|I])([\d\.\-]+)")


class cncprm():
    def __init__(self, path: str|None|Path):
        if isinstance(path, str):
            path = Path(path)
        self.fullbody = {"data":[], "index":{}}
        if path is not None:
            self.PrmToJson(path)
        
    def PrmToJson(self, path: str):
        # 入力ファイルを読み込み
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        for line in lines:
            x = self.prmlineToJson(line)
            if x is None:
                continue
            self.fullbody["data"].append(x[0])
            self.fullbody["index"].update(x[1])

    def prmlineToJson(self, prm_line):
        prm_line = prm_line.strip()

        # N番号を抽出
        print(prm_line)
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
                _d = self.extract_axis_values(Q_data_part)
                if _d is not None:
                    _d.update(
                        {
                            "N_number": N_number,
                            "Q_number": Q_number,
                            "raw_line": prm_line
                        }
                    )
                    return _d, {_d["N_number"]["N_index"]: _d}
            
    def extract_axis_values(self, data_part):
        axis_values = []
        print(data_part)
        axis_letter, axis_index, value_letter, value= ('', 0, '', '')
        if pattern_AxValue.search(data_part):
            # 軸と値のペアを抽出
            for match in pattern_AxValue.finditer(data_part):
                axis_letter, axis_index, value_letter, value = match.groups()
                axis_values.append(
                    {"axis_letter": f"{axis_letter}", "axis_index": int(axis_index),
                    "value_letter": value_letter, "value": f"{value}"}
                )
                axis_type = f"AXIS_TYPE_{axis_letter}"
                value_type = f"VALUE_TYPE_{value_letter}"
        elif pattern_OnlyValue.search(data_part):
            matchValues = pattern_OnlyValue.findall(data_part)[0]
            print(matchValues)
            value_letter, value = matchValues[0], matchValues[1]
            axis_values.append(
                {"axis_letter": axis_letter, "axis_index": int(axis_index),
                "value_letter": value_letter,"value": f"{value}"}
            )
            axis_type = f"AXIS_TYPE_NONE"
            value_type = f"VALUE_TYPE_{value_letter}"
        else:
            raise ValueError(f"errValue: {data_part}")

        # 軸インデックス順にソート
        axis_values.sort(key=lambda x: x["axis_index"] if x["axis_index"]!='' else 0)

        # format判定
        values_only = [v["value"] for v in axis_values]
        if all(len(v) == 8 and set(v) <= {"0", "1"} for v in values_only):
            fmt = "Bit_8"
        elif any("." in v for v in values_only):
            fmt = "Decimal"
        else:
            fmt = "Integer"

        # 結果を格納
        return {
                "axis_type": axis_type,
                "value_type": value_type,
                "format": fmt,
                "body": axis_values
            }
        
    def output_Json(self, path: str = "parameter.josn"):
        # JSONファイルに保存
        if not self.data:
            return None
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)



if __name__ == '__main__':
    filepath = Path("data/CNC-PARA.TXT")
    print(filepath.resolve())
    p = cncprm(filepath)
    
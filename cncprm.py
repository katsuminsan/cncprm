import re
import json

class fncprm:
    msg1 = 'fncprm: Axis-index error. Only decimal can be given'
    re_prm = re.compile('(^N[0-9]{1,5})(Q[1])')
    re_A = re.compile('A[0-9]{1,2}[^A]*')
    re_S = re.compile('S[0-9]{1,2}[^S]*')
    re_T = re.compile('T[0-9]{1,2}[^T]*')
    re_L = re.compile('L[0-9]{1,2}[^L]*')
    re_PM = re.compile('[P|M]')
    ZEN2HAN = str.maketrans(''.join(chr(0xff01 + i) for i in range(94)), ''.join(chr(0x21 + i) for i in range(94)))

    def __iter__(self):
        """イテレータとしての振る舞いを定義します"""
        return iter(sorted(self.odc_prm.items()))

    def __len__(self):
        """パラメータの総数を返します"""
        return len(self.odc_prm)

    def get_parameter_list(self):
        """GUIでの表示用にパラメータリストを生成します"""
        result = []
        for prm_num, prm_data in sorted(self.odc_prm.items()):
            param_info = {
                "number": prm_data["head"]["PrmNumber"],
                "type": prm_data["head"]["Type"],
                "axes": []
            }
            
            for axis in prm_data["body"]:
                param_info["axes"].append({
                    "index": axis["Index"],
                    "value": axis["Value"]
                })
            
            result.append(param_info)
        return result

    def get_axis_parameters(self, axis_index):
        """特定の軸に関連するパラメータのみを取得します"""
        result = []
        axis_str = str(axis_index)
        
        for prm_num, prm_data in sorted(self.odc_prm.items()):
            for axis in prm_data["body"]:
                if axis["Index"].endswith(axis_str):
                    result.append({
                        "number": prm_data["head"]["PrmNumber"],
                        "type": prm_data["head"]["Type"],
                        "axis": axis["Index"],
                        "value": axis["Value"]
                    })
                    break
        return result

    def get_formatted_display(self):
        """GUIでの表示用に整形された文字列を返します"""
        lines = []
        for prm_num, prm_data in sorted(self.odc_prm.items()):
            head = prm_data["head"]
            line = f"{head['PrmNumber']} ({head['Type']}): "
            
            axis_values = []
            for axis in prm_data["body"]:
                axis_values.append(f"{axis['Index']}={axis['Value']}")
            
            line += ", ".join(axis_values)
            lines.append(line)
        
        return "\n".join(lines)
    
    def __init__(self, filepath =None):
        self.odc_prm = {}
        if filepath != None:
            self.load(filepath)
        
    def loads(self, prm_lines):
        """文字列からパラメータをロードします"""
        buf_prm = prm_lines
        lines = buf_prm.split('\n')
        
        for line in lines:
            parsed_data = self.line_load(line)
            if parsed_data and "head" in parsed_data:
                prm_num = parsed_data["head"]["PrmNumber"]
                self.odc_prm[prm_num] = parsed_data
        
    def load(self, filepath):
        """ファイルからパラメータをロードします"""
        with open(filepath) as f:
            for line in f:
                parsed_data = self.line_load(line)
                if parsed_data and "head" in parsed_data:
                    prm_num = parsed_data["head"]["PrmNumber"]
                    self.odc_prm[prm_num] = parsed_data
    
    def overwrites(self, cncprms):
    #overwrite odc_prm to cncprm-txt
        buf_prm = cncprms
        lines = buf_prm.split('\n')
        ov_odc_prm = {}
        
        for line in lines:
            prm_line = self.line_load(line)
            if len(prm_line) != 0:
                ov_odc_prm[prm_line[0][0]] = prm_line
        
        self.deepupdate(self.odc_prm, ov_odc_prm)
        
    def overwrite(self, obj_fncprm):
    #overwrite odc_prm to fnc_object
        if isinstance(obj_fncprm, fncprm):
            self.deepupdate(self.odc_prm, obj_fncprm.odc_prm)
        else:
            raise TypeError('fncprm.overwrite(): arg 1 must be a cncprm.fncprm object')
        
    def dump(self):
    # Change odc_prm to cncprm-txt file
        _d = self.dumps()
        return f'% \n{_d}% \n'
        
    def dumps(self):
        """パラメータをCNCフォーマットの文字列に変換します"""
        dmp_prm = []
        try:
            for prm_data in self.odc_prm.values():
                head = prm_data["head"]
                body = prm_data["body"]
                
                line = head["PrmNumber"] + head["Type"]
                for axis in body:
                    line += axis["Index"] + axis["Value"]
                    
                dmp_prm.append(line)
                
            return ' \n'.join(dmp_prm) + ' \n'
            
        except:
            return None
        
    def del_prm(self, PrmNumber=None, Ax_index=0, unit_index=1):
        """パラメータまたは特定の軸データを削除します"""
        if PrmNumber is None:
            return False

        # パラメータ番号の正規化
        if str(PrmNumber).isdecimal():
            prm_num = f'N{int(PrmNumber):05d}'
        else:
            num = str(PrmNumber).upper().translate(fncprm.ZEN2HAN)
            if num.startswith('N') and len(num) <= 5:
                prm_num = f'N{int(num[1:]):05d}'
            elif num.startswith('N') and len(num) == 6:
                prm_num = num
            else:
                prm_num = num

        # パラメータが存在するか確認
        if prm_num not in self.odc_prm:
            return False

        # 軸インデックスが指定されている場合
        if Ax_index != 0:
            if not str(Ax_index).isdecimal():
                raise Exception(fncprm.msg1)
            
            axid = str(Ax_index)
            prm_data = self.odc_prm[prm_num]
            
            # 特定の軸を削除
            new_body = [axis for axis in prm_data["body"] if not axis["Index"].endswith(axid)]
            
            if len(new_body) != len(prm_data["body"]):
                if new_body:
                    prm_data["body"] = new_body
                else:
                    del self.odc_prm[prm_num]
                return True
            
            # 単一軸パラメータで軸インデックスが1以下の場合
            if len(prm_data["body"]) == 1 and int(axid) <= 1:
                del self.odc_prm[prm_num]
                return True
                
            return False
        else:
            # パラメータ全体を削除
            del self.odc_prm[prm_num]
            return True
        
    def PrmValue(self, PrmNumber=None, Ax_index=0, unit_index=1):
        """パラメータ値を取得します"""
        if PrmNumber is None:
            return None

        # パラメータ番号の正規化
        if str(PrmNumber).isdecimal():
            prm_num = f'N{int(PrmNumber):05d}'
        else:
            num = str(PrmNumber).upper().translate(fncprm.ZEN2HAN)
            if num.startswith('N') and len(num) <= 5:
                prm_num = f'N{int(num[1:]):05d}'
            elif num.startswith('N') and len(num) == 6:
                prm_num = num
            else:
                prm_num = num

        # パラメータの検索
        if prm_num not in self.odc_prm:
            return None

        prm_data = self.odc_prm[prm_num]

        # 軸インデックスが指定されている場合
        if Ax_index != 0:
            if not str(Ax_index).isdecimal():
                raise Exception(fncprm.msg1)
            
            axid = str(Ax_index)
            for axis in prm_data["body"]:
                if axis["Index"].endswith(axid):
                    return axis["Value"]
            
            # 単一軸パラメータで軸インデックスが1以下の場合
            if len(prm_data["body"]) == 1 and int(axid) <= 1:
                return prm_data["body"][0]["Value"]
            
            return None

        # 全軸のデータを辞書形式で返す
        return {axis["Index"]: axis["Value"] for axis in prm_data["body"]}
        
    def deepupdate(self, base_dict, ov_dict):
        """2つのパラメータ辞書を深い更新で結合します"""
        for k, v in ov_dict.items():
            if k not in base_dict:
                base_dict[k] = v
                continue

            # ヘッダー情報の更新
            base_dict[k]["head"].update(v["head"])

            # ボディ（軸データ）の更新
            base_indices = {axis["Index"]: i for i, axis in enumerate(base_dict[k]["body"])}
            
            for new_axis in v["body"]:
                if new_axis["Index"] in base_indices:
                    # 既存の軸データを更新
                    base_dict[k]["body"][base_indices[new_axis["Index"]]] = new_axis
                else:
                    # 新しい軸データを追加
                    base_dict[k]["body"].append(new_axis)

        return base_dict
        
    def line_load(self, oneline):
        """
        CNCパラメータの1行を解析してJSON構造に変換します
        戻り値の形式:
        {
            "head": {"PrmNumber": "N00000", "Type": "Q1"},
            "body": [{"Index": "L1", "Value": "P00000000"}, ...]
        }
        """
        try:
            line_buf = oneline.strip()
            if not line_buf.startswith('N'):
                return {}

            # ヘッダー部分（パラメータ番号とタイプ）の解析
            prm_match = fncprm.re_prm.findall(line_buf)
            if not prm_match:
                return {}
            
            prm_num, prm_type = prm_match[0]
            head = {
                "PrmNumber": prm_num,
                "Type": prm_type
            }

            # ボディ部分（軸データ）の解析
            line_buf = line_buf[len(prm_num + prm_type):]
            body = []

            if line_buf.startswith(('A', 'S', 'L', 'T')):
                # 複数軸パラメータの場合
                if line_buf[0] == 'A':
                    axis_data = fncprm.re_A.findall(line_buf)
                elif line_buf[0] == 'S':
                    axis_data = fncprm.re_S.findall(line_buf)
                elif line_buf[0] == 'L':
                    axis_data = fncprm.re_L.findall(line_buf)
                elif line_buf[0] == 'T':
                    axis_data = fncprm.re_T.findall(line_buf)

                for axis in axis_data:
                    PM_pos = fncprm.re_PM.search(axis)
                    if PM_pos:
                        index = axis[:PM_pos.start()]
                        value = axis[PM_pos.start():]
                        body.append({
                            "Index": index,
                            "Value": value
                        })
            else:
                # 単一軸パラメータの場合
                if line_buf.startswith(('P', 'M')):
                    body.append({
                        "Index": "1",
                        "Value": line_buf
                    })

            if head["PrmNumber"] and body:
                return {
                    "head": head,
                    "body": body
                }
            return {}

        except:
            return {}
    def to_json(self):
        return json.dumps(self.odc_prm, indent=4)

##    def axid_scan(self, axid, ax_lists):
##        return ax_lists[axid]

if __name__ == '__main__':
    import os
    cncfile = os.path.join('data','CNC-PARA.TXT')
    fnc = fncprm(cncfile)
    print(fnc.odc_prm)



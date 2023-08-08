import re

class fncprm:
    msg1 = 'fncprm: Axis-index error. Only decimal can be given'
    re_prm = re.compile('(^N[0-9]{1,5})(Q[1])')
    re_A = re.compile('A[0-9]{1,2}[^A]*')
    re_S = re.compile('S[0-9]{1,2}[^S]*')
    re_T = re.compile('T[0-9]{1,2}[^T]*')
    re_L = re.compile('L[0-9]{1,2}[^L]*')
    re_PM = re.compile('[P|M]')
    ZEN2HAN = str.maketrans(''.join(chr(0xff01 + i) for i in range(94)), ''.join(chr(0x21 + i) for i in range(94)))
    def __init__(self, filepath =None):
        self.odc_prm = {}
        if filepath != None:
            self.load(filepath)
        
    def loads(self, prm_lines):
    #load to strings.
        
        #If the data already exists, all Prm_line are replaced with prm_lines.
        
        buf_prm = prm_lines
        prm_line =[]
        prm = ''
        lines = buf_prm.split('\n')
        
        for line in lines:
            prm_line = self.line_load(line)
            if len(prm_line) != 0:
                self.odc_prm[prm_line[0][0]] = prm_line
        
    def load(self, filepath):
    #load to txt_file
        #If the data already exists, all Prm_line are replaced with Prmlines in the filepath.
        
        prm_line =[]
        prm = ''
        with open(filepath) as f:
            for line in f:
                prm_line = self.line_load(line)
                if len(prm_line) != 0:
                    self.odc_prm[prm_line[0][0]] = prm_line
    
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
        if isinstace(obj_fncprm, cncprm.fncprm):
            ov_odc_prm = obj_fncprm.odc_prm
            self.deepupdate(self.odc_prm, obj_fncprm.odc_prm)
        else:
            raise TypeError('fncprm.overwrite(): arg 1 must be a cncprm.fncprm object')
        
    def dump(self):
    # Change odc_prm to cncprm-txt file
        _d = self.dumps()
        return f'% \n{_d}% \n'
        
    def dumps(self):
    #Change odc_prm to cncprm-format
        dmp_prm = []
        prm_head = ''
        prm_body = ''
        try:
            dmp_buf = self.odc_prm.values()
            dmp_prm_append = dmp_prm.append
            for line_buf in dmp_buf:
                prm_head = ''.join(line_buf[0]) # get prm_no
                
                if isinstance(line_buf[1], dict):
                    prm_body = ''.join([lb_k + lb_v for lb_k,lb_v in zip(line_buf[1].keys(), line_buf[1].values())]) # get prm_value, multi-axis case ('L1L2, A1A2 etc...')
                else:
                    prm_body = line_buf[1] # get prm_value, single-axis case ('P-value')
                
                dmp_prm_append(prm_head + prm_body) # Add_dmp
                
            return ' \n'.join(dmp_prm) + ' \n' # Add Lf,  [a, b, c] --> ('a [\n]b [\n]c [\n]')
            
        except:
            return None
        
    def del_prm(self, PrmNumber = None, Ax_index = 0, unit_index = 1):
    #Search Prm in odc_prm and delete it
        if PrmNumber != None:
            PRM_v = ''
            
        
    def PrmValue(self, PrmNumber = None, Ax_index = 0, unit_index = 1):
    #Search Prm in odc_prm
        
        # Ax_index type is only integer. if you set not int. to Ax_index, PrmValue give All index then type of dict to you.
        
        
        #
        # PrmNumber get
        #
        if PrmNumber != None:
            if str(PrmNumber).isdecimal():
                num = PrmNumber
                prm_num = 'N%05d' % int(num) # 'N'+ integer*5   example:= 'N00001' (integer = 1)
            else:
                num = str(PrmNumber).upper() # LangType larger
                num = num.translate(fncprm.ZEN2HAN) # LangType harf_size
                if bool(num[0] == 'N' and len(num) <= 5):
                    num = num[1:]
                    prm_num = 'N%05d' % int(num)
                elif bool(num[0] == 'N' and len(num) == 6):
                    prm_num = num
                else:
                    prm_num = num
                    
            PRM_v = self.odc_prm[prm_num]
            
        else:
            return None
            
        #
        # Ax_index get
        # axid is Type of integer
        #
        if Ax_index != 0:
            if str(Ax_index).isdecimal(): # int only, false is return all_index_data
                axid = int(Ax_index) # zero head remove
                
                if ('L' + str(axid)) in PRM_v[1]:
                    ax_v = PRM_v[1]['L' + str(axid)]
                    
                elif ('A' + str(axid)) in PRM_v[1]:
                    ax_v = PRM_v[1]['A' + str(axid)]
                    
                elif ('S' + str(axid)) in PRM_v[1]:
                    ax_v = PRM_v[1]['S' + str(axid)]
                    
                elif ('M' + str(axid)) in PRM_v[1]:
                    ax_v = PRM_v[1]['M' + str(axid)]
                    
                elif isinstance(PRM_v[1], str) and (axid <= 1):
                    ax_v = PRM_v[1]
                #
                # ax_v axis-values Buffa get
                #
                prm_ax = re.sub(r'\D', '', ax_v)
                
                if len(ax_v) != 0:
                    prm_ax = ax_v
                else:
                    prm_ax = None
                
            else:
                raise Exception(fncprm.msg1)
                
        else:
            prm_ax = PRM_v[1]
            
        try:
            
            return prm_ax
            
        except:
            return None
        
    def deepupdate(self, base_dict, ov_dict):
        for k, v in ov_dict.items():
            if isinstance(v[1], dict):
                for ov_k, ov_v in v[1].items():
                    try:
                        base_dict[k][1][ov_k] = ov_v # update prm_value, multi-axis case ('L1L2, A1A2 etc...')
                    except:
                        base_dict[k] = v
            else:
                try:
                    base_dict[k][1] = v[1] # update prm_value, single-axis case ('P-value')
                except:
                    base_dict[k] = v
        
        return base_dict
        
    def line_load(self, oneline):
    #change odc_prm to cncprm_txt
        try:
            line_buf = oneline
            line_buf = line_buf.strip()
            list_body = {}
            body = []
            parse_line = []
            PM_pos = 0
            if line_buf[0] == 'N':
                #% jogai prmline dake
                prm = list(fncprm.re_prm.findall(line_buf)[0])
                
                #prm jogai axisline dake
                line_buf = line_buf[len(''.join(prm)):]
                
                if line_buf[0] == 'A':
                    body = fncprm.re_A.findall(line_buf)
                    
                elif line_buf[0] == 'S':
                    body = fncprm.re_S.findall(line_buf)
                    
                elif line_buf[0] == 'L':
                    body = fncprm.re_L.findall(line_buf)
                    
                elif line_buf[0] == 'T':
                    body = fncprm.re_T.findall(line_buf)
                    
                elif line_buf[0] == 'P':
                    list_body = line_buf
                    
                elif line_buf[0] == 'M':
                    list_body = line_buf
                    
                else:
                    list_body = {}
                    
                
                #sozai
                if len(list_body) == 0: ##P-type goto else  DEBUG
                    for x in body:
                        PM_pos = fncprm.re_PM.search(x).start()
                        if PM_pos != None:
                            list_body[x[:PM_pos]] = x[PM_pos:]
                            
                
                if bool(prm[0] != '' and len(list_body) != 0):
                    parse_line = [prm, list_body]
                    return parse_line
                    
                else:
                    return {}
            else:
                return {}
        except:
            return {}
                        

##    def axid_scan(self, axid, ax_lists):
##        return ax_lists[axid]

if __name__ == '__main__':
    import json
    import os
    cncfile = os.path.join('data','b5plus_CNC-PARA.TXT')
    Ad_cncfile = os.path.join('data','Add_CNC-PARA.TXT')
    jsfile = os.path.join('data','b5plus.json')
    Ad_jsfile = os.path.join('data','Ad_b5plus.json')
    re_jsfile = os.path.join('data','re_b5plus.json')
    
    dmpfile = os.path.join('data','dmp.txt')
    Ad_dmp = os.path.join('data','Ad_dmp.txt')
    re_dmp = os.path.join('data','re_dmp.txt')
    
    fnc = fncprm(cncfile)
    Ad_fnc = fncprm(Ad_cncfile)
    
    with open(dmpfile, 'w') as f:
        f.write(fnc.dump())
        
    with open(Ad_dmp, 'w') as f:
        f.write(Ad_fnc.dump())
    
##    with open(re_dmp, 'w') as f:
##        re_dump.dump()
    
##    Dmp = Ad_fnc.dump()
    
##    with open(jsfile, 'w') as f:
##        json.dump(fnc.odc_prm, f, sort_keys = True, ensure_ascii = True, indent=4)
##    
##    with open(Ad_jsfile,'w') as f:
##        json.dump(Ad_fnc.odc_prm, f, sort_keys = True, ensure_ascii = True, indent = 4)
##    
##    with open(jsfile,'r') as f:
##        dc1 = json.load(f)
##    with open(Ad_jsfile,'r') as f:
##        dc2 = json.load(f)
##    
##    dc1.update(dc2)
##    
##    with open(re_jsfile,'w') as f:
##        json.dump(dc1, f, sort_keys = True, ensure_ascii = True, indent = 4)
##    
##    print(json.dumps(fnc.odc_prm, sort_keys = True, indent = 4))
##    print(fnc.PrmValue(1))


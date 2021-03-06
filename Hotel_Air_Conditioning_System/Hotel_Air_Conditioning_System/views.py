"""
Routes and views for the flask application.
"""

import os

from datetime import datetime
from flask import request,send_from_directory, redirect, request
from Hotel_Air_Conditioning_System.Controller import *
from Hotel_Air_Conditioning_System import app
from Hotel_Air_Conditioning_System import dao
import json
from Hotel_Air_Conditioning_System.impl import gDict
from flask_apscheduler import APScheduler
from flask import current_app,Response

def cors_resp(resp_text):
    resp = Response(resp_text)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] =  "X-GOTHER, Content-Type"
    resp.headers["Access-Control-Max-Age"] = "86400"
    return resp

##兼容QT转发模块
@app.route('/', methods=['GET','POST'])
def re_route():
    if request.method == 'GET':
        return redirect('./frontend/index.html')
    else:
        data = request.data
        params = json.loads(data)
        # params = request.get_json()
        print(params)
        if params.get("actorType", 0) == 0:
            return "actorType not found", 400
        if params.get("requestType", 0) == 0:
            return "requestType not found", 400
        actor = params["actorType"]
        req_type = params["requestType"]
        # 对无法重定向的顾客端单独处理
        if actor == "cos":
            if params.get("roomID", 0) == 0:
                return "roomID not found", 400
            roomID = params["roomID"]
            oc = OperateController.OperateController()
            if req_type == "on":
                return cors_resp(oc.RequestOn(roomID))
            elif req_type == "ref":
                return cors_resp(oc.Refresh(roomID))
            elif req_type == "spd":
                target_spd = params.get("trg","M")
                return cors_resp(oc.ChangeFanSpeed(roomID, target_spd))
            elif req_type == "tmp":
                target_temp = params.get("trg",0)
                return cors_resp(oc.ChangeTargetTemp(roomID, target_temp))
            elif req_type == "off":
                return cors_resp(oc.RequestOff(roomID))
        return redirect('./api/'+actor+'/'+req_type, code=307)



## 资源文件下载
@app.route('/frontend/static/<path:filename>')
def resource(filename):
    dirpath = os.path.join(app.root_path, "frontend/static") #定位至后台程序所在目录的static文件下
    return send_from_directory(dirpath, filename, as_attachment=True)

@app.route('/download/<path:filename>')
def download(filename):
    dirpath = os.path.join(app.root_path)
    return send_from_directory(dirpath, filename, as_attachment=True)



## 页面路由
@app.route('/frontend/<path:pagename>')
def page(pagename):
    path = os.path.join(app.root_path,"frontend/"+pagename)
    f = open(path, encoding='utf-8')
    return f.read()




## 接口路由

    


## 管理员
# 开机
@app.route('/api/adm/on', methods=['POST'])
def powerOn():
    suc = StartUPController.StartUPController()
    return cors_resp(suc.PowerOn())

# 设置运行参数
@app.route('/api/adm/para', methods=['POST'])
def setPara():
    data = request.data
    params = json.loads(data)
    mode = params.get("mode", 0)
    temp_highLimit = params.get("tmpH", 0)
    temp_lowLimit = params.get("tmpL", 0)
    default_targetTemp = params.get("tmpD", 0)
    feeRate_H = params.get("rateH", 0)
    feeRate_M = params.get("rateM", 0)
    feeRate_L = params.get("rateL", 0)
    if mode == 0 | temp_highLimit ==0 | temp_lowLimit ==0 | default_targetTemp == 0 | feeRate_H == 0 | feeRate_L == 0 | feeRate_M ==0:
        return "wrong attr", 400
    suc = StartUPController.StartUPController()
    return cors_resp(suc.SetPara(mode, temp_highLimit, temp_lowLimit, default_targetTemp, feeRate_H,feeRate_M,feeRate_L))

# 启动
@app.route('/api/adm/start', methods=['POST'])
def StartUp():
    suc = StartUPController.StartUPController()
    return cors_resp(suc.StartUp())

# 查看房间状态
@app.route('/api/adm/check', methods=['POST'])
def CheckRoomState():
    data = request.data
    params = json.loads(data)
    csc = CheckStateController.CheckStateController()
    return cors_resp(csc.CheckRoomState())




## 顾客
# 显示数据刷新
@app.route('/api/cos/ref', methods=["POST"])
def refresh():
    data = request.data         
    params = json.loads(data)
    if params.get("roomID", 0) == 0:
        return "roomID not found", 400
    roomID = params["roomID"]
    oc = OperateController.OperateController()
    return cors_resp(oc.Refresh(roomID))
    

# 开空调
@app.route('/api/cos/on', methods=['POST'])
def RequestOn():
    data = request.data
    params = json.loads(data)
    room_id = params.get("roomID",0)
    if room_id == 0:
        return "roomID not found", 400
    oc = OperateController.OperateController()
    return cors_resp(oc.RequestOn(room_id))

# 关空调
@app.route('/api/cos/off', methods=['POST'])
def RequestOff():
    data = request.data
    params = json.loads(data)
    room_id = params.get("roomID",0)
    if room_id == 0:
        return "roomID not found", 400
    oc = OperateController.OperateController()
    return cors_resp(oc.RequestOff(room_id))

# 调目标温度
@app.route('/api/cos/tmp', methods=['POST'])
def ChangeTargetTemp():
    data = request.data
    params = json.loads(data)
    room_id = params.get("roomID",0)
    target_temp = params.get("trg",0)
    if room_id == 0:
        return "roomID not found", 400
    if target_temp == 0:
        return "Invalid Request", 400
    oc = OperateController.OperateController()
    return cors_resp(oc.ChangeTargetTemp(room_id, target_temp))

# 调风速
@app.route('/api/cos/spd', methods=['POST'])
def ChangeFanSpeed():
    data = request.data
    params = json.loads(data)
    room_id = params.get("roomID",0)
    target_spd = params.get("trg",0)
    if room_id == 0:
        return "roomID not found", 400
    if target_spd == 0:
        return "Invalid Request", 400
    oc = OperateController.OperateController()
    return cors_resp(oc.ChangeFanSpeed(room_id, target_spd))




## 前台
# 获取账单
@app.route('/api/inf/inv', methods=['POST'])
def create_invoice():
    data = request.data
    params = json.loads(data)
    if params.get("roomID", 0) == 0:
        return "roomID not found", 400
    roomID = params["roomID"]
    
    cIc = CreateInvoiceController.CreateInvoiceController()
    Invoice = cIc.CreateInvoice(roomID)
    return cors_resp(Invoice)

# 获取详单
@app.route('/api/inf/rdr', methods=['POST'])
def create_rdr():
    data = request.data
    params = json.loads(data)
    if params.get("roomID", 0) == 0:
        return "roomID not found", 400
    roomID = params["roomID"]
    cRDRc = CreateRDRController.CreateRDRController()
    RDR = cRDRc.CreateRDR(roomID)
    return cors_resp(RDR)

# 打印
@app.route('/api/inf/print', methods=['POST'])
def print_inv_rdr():
    data = request.data
    params = json.loads(data)
    room_id = params.get("id")
    typee = params.get("type")
    print(params)
    dateIn = datetime.strptime(params.get("dateIn"), "%Y-%m-%d %H:%M:%S")
    dateOut = datetime.strptime(params.get("dateOut"),"%Y-%m-%d %H:%M:%S")
    base_fname = typee+"_"+str(room_id)+"_"+datetime.strftime(dateIn,"%Y-%m-%d-%H%M%S")+"-"+datetime.strftime(dateOut,"%Y-%m-%d-%H%M%S")+"_json.txt"
    return cors_resp("download/"+typee+"/"+base_fname)



## 经理
# 获取报表
@app.route('/api/mng/rep', methods=['POST'])
def QueryReport():
    data = request.data
    params = json.loads(data)
    rep_type = params.get("type", 0)
    until = datetime.strptime(params.get("until","1970-1-1"),"%Y-%m-%d %H:%M:%S")
    # until = until_full.date()
    print(until)
    if rep_type == 0:
        return "Invalid Request", 400
    if until == 0:
        return "Invalid Request", 400
    rc = ReporterController.ReporterController()
    res = rc.QueryReport(rep_type, until)
    return cors_resp(res)

@app.route('/api/mng/print', methods=['POST'])
def PrintReport():
    data = request.data
    params = json.loads(data)
    type_report = params.get("type", 0)
    until_full = params.get("until","1970-1-1")
    until = str(datetime.strptime(until_full,"%Y-%m-%d %H:%M:%S").date())
    base_fname = "rep_"+type_report+"_"+until+"_json.txt"
    return cors_resp("download/rep/"+base_fname)






## 测试路由
# @app.route('/api/inf/invoice/<id>')
# def invoice(id):
#     from Hotel_Air_Conditioning_System.dao.iInvoiceDAO import iInvoiceDAO
#     idao = iInvoiceDAO()
#     return cors_resp(str(idao.GetTotal(203, "2019-05-24", "2019-05-25")))

# 查看系统当前状态
@app.route('/api/state')
def show_state():
    res = {}
    res["gDict_leys"] = str(gDict.keys())
    rooms = gDict.get("rooms")
    res["rooms"] = []
    for room in rooms.list_room:
        roominfo = {}
        roominfo["room_id"] = room.room_id
        roominfo["cur_tmp"] = room.cur_tmp
        roominfo["last_op_time"] = str(room.last_op_time)
        roominfo["state"] = room.state
        roominfo["trg_tmp"] = room.trg_tmp
        res["rooms"].append(roominfo)
    serv_pool = gDict.get("serv_pool", 0)
    if serv_pool != 0:
        res["serv_pool_state"] = serv_pool.state
        res["num_service"] = len(serv_pool.serv_list)
        for serv in serv_pool.serv_list:
            res["service"+str(serv.service_id)] = {}
            res["service"+str(serv.service_id)]["is_working"] = serv.is_working
            res["service"+str(serv.service_id)]["room_id"] = serv.room_id
            res["service"+str(serv.service_id)]["trg_tmp"] = serv.trg_tmp
    else:
        res["serv_pool"] = 0
    schedule = gDict.get("schedule", 0)
    if schedule != 0:
        res["serv_queue"] = {}
        res["wait_queue"] = {}
        res["serv_queue"]["length"] = len(schedule.serv_queue)
        for serv in schedule.serv_queue:
            res["serv_queue"]["item"+str(serv.service_id)] = {}
            res["serv_queue"]["item"+str(serv.service_id)]["room_id"] = serv.room_id
            res["serv_queue"]["item"+str(serv.service_id)]["service_id"] = serv.service_id
            res["serv_queue"]["item"+str(serv.service_id)]["speed"] = serv.speed
            res["serv_queue"]["item"+str(serv.service_id)]["start_time"] = str(serv.start_time)
        res["wait_queue"]["length"] = len(schedule.wait_queue)
        for wait in schedule.wait_queue:
            res["wait_queue"]["item"+str(schedule.wait_queue.index(wait))] = {}
            res["wait_queue"]["item"+str(schedule.wait_queue.index(wait))]["room_id"] = wait.room_id
            res["wait_queue"]["item"+str(schedule.wait_queue.index(wait))]["speed"] = wait.speed
            res["wait_queue"]["item"+str(schedule.wait_queue.index(wait))]["start_time"] = str(wait.start_time)
    else:
        res["wait_pool"] = 0
    res["settings"] = gDict.get("settings", 0)
    print(res)
    return cors_resp(json.dumps(res))


@app.route('/api/job')
def joblist():
    return cors_resp(str(current_app.apscheduler.get_jobs()))
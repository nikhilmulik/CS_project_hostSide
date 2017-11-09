import codecs
import os
import sys
import traceback
import win32con
import win32evtlog
import win32evtlogutil
import winerror
import logging
import re
import string
import ctypes
import bluetooth
import ConfigParser
import time


def date2sec(evt_date):
    regexp = re.compile('(.*)\\s(.*)')
    reg_result = regexp.search(evt_date)
    date = reg_result.group(1)
    the_time = reg_result.group(2)
    (mon, day, yr) = map(lambda x: string.atoi(x), string.split(date, '/'))
    (hr, min, sec) = map(lambda x: string.atoi(x), string.split(the_time, ':'))
    tup = [yr, mon, day, hr, min, sec, 0, 0, 0]
    sec = time.mktime(tup)
    return sec


# ----------------------------------------------------------------------
def getAllEvents(server, logtypes, basePath):
    if not server:
        serverName = "localhost"
    else:
        serverName = server
    for logtype in logtypes:
        path = os.path.join(basePath, "%s_%s_log.log" % (serverName, logtype))
        getEventLogs(server, logtype, path)
    return


# ----------------------------------------------------------------------
def getEventLogs(server, logtype, logPath):
    log = codecs.open(logPath, encoding='utf-8', mode='w')

    begin_sec = time.time()
    begin_time = time.strftime('%H:%M:%S  ', time.localtime(begin_sec))
    hand = win32evtlog.OpenEventLog(server, logtype)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    events = win32evtlog.ReadEventLog(hand,flags,0)
    evt_dict={win32con.EVENTLOG_AUDIT_FAILURE:'EVENTLOG_AUDIT_FAILURE',
              win32con.EVENTLOG_AUDIT_SUCCESS:'EVENTLOG_AUDIT_SUCCESS',
              win32con.EVENTLOG_INFORMATION_TYPE:'EVENTLOG_INFORMATION_TYPE',
              win32con.EVENTLOG_WARNING_TYPE:'EVENTLOG_WARNING_TYPE',
              win32con.EVENTLOG_ERROR_TYPE:'EVENTLOG_ERROR_TYPE'}
    try:
        events = 1
        while events:
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            for ev_obj in events:
                the_time = ev_obj.TimeGenerated.Format()  # '12/23/99 15:54:09'
                seconds = date2sec(the_time)
                if seconds < begin_sec - 15: break
                evt_id = str(winerror.HRESULT_CODE(ev_obj.EventID))
                event_list = [event for event in events if event.EventID == "27035"]
                if event_list:
                    print 'Event Category:', event_list[0].EventCategory

                computer = str(ev_obj.ComputerName)
                cat = ev_obj.EventCategory
                record = ev_obj.RecordNumber
                msg = win32evtlogutil.SafeFormatMessage(ev_obj, logtype)

                source = str(ev_obj.SourceName)
                if not ev_obj.EventType in evt_dict.keys():
                    evt_type = "unknown"
                else:
                    evt_type = str(evt_dict[ev_obj.EventType])
                # logging.info("Event Date/Time: %s\n" % the_time)
                # logging.info("Event ID / Type: %s / %s\n" % (evt_id, evt_type))

                if evt_id in ['4625']:  # An account failed to log on
                    print "XXXXXXXXXXXXXXXXxxxxxxxxx--------FAILED LOGIN!!!"
                    begin_sec = time.time()
                    the_time = ev_obj.TimeGenerated.Format()
                    seconds = date2sec(the_time)
                    os.startfile(os.getcwd()+'\\dist\\capture_me.exe')
                    logging.info("Record #%s" % record)
                    logging.info("Source: %s" % source)
                    logging.info(msg)
                    logging.info('-' * 80)
    except:
        message = traceback.print_exc(sys.exc_info())
        logging.error(message)


if __name__ == "__main__":
    server = None  # None = local machine
    logTypes = ["Security"]
    counter = 0
    logPath = os.path.join(os.getcwd(), "%s_log.log" % (logTypes[0]))
    logging.basicConfig(filename=logPath, level=logging.INFO)
    config = ConfigParser.ConfigParser()
    config.read("config.cfg")
    device_id = config.get('Device', 'id')
    scan_status = config.get('Device', 'status')
    while True:
        counter += 1
        print '->', counter
        getAllEvents(server, logTypes, os.getcwd())
        if False: #scan_status:
            deathstat = bluetooth.discover_devices()
            if device_id not in deathstat:
                ctypes.windll.user32.LockWorkStation()



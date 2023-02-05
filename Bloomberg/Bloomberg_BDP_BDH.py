import blpapi

class DataQuotaLimitError(Exception):
    """
    Raised when the user reach a Bloomberg quota limit.
    """
    pass

class Bloomberg:
    def __init__(self):
        self.session_options = blpapi.SessionOptions()
        self.session_options.setServerHost("localhost")
        self.session_options.setServerPort(8194)

    def _handle_error(self, msg):
        if msg.hasElement("responseError"):
            error = msg.getElement("responseError")
            if error.hasElement("category"):
                if error.getElement("category").getValue() == 'LIMIT':
                    raise DataQuotaLimitError(error.getElement("message").getValue())
                elif error.getElement("category").getValue() == 'BAD_ARGS':
                    raise DataQuotaLimitError(error.getElement("message").getValue())
                elif error.getElement("category").getValue() == 'BAD_FLD':
                    raise DataQuotaLimitError(error.getElement("message").getValue())
                else:
                    raise DataQuotaLimitError("Unknown error, please try again.")

    def _start_session(self):
        session = blpapi.Session(self.session_options)

        # Start a Session
        if not session.start():
            print("ERROR: Failed to start session.")
            return None
        else:
            return session

    def BDH(self, isins, fields, start_date, end_date=None):
        session = self._start_session()
        if session:
            if len(isins) == 0:
                print("No securities attached.")
                return

            if len(fields) == 0:
                print("No fields included.")
                return

            if not session.openService("//blp/refdata"):
                print("Failed to open //blp/refdata")
                return

            refDataService = session.getService("//blp/refdata")
            request = refDataService.createRequest("HistoricalDataRequest")

            #request.set("periodicityAdjustment", "ACTUAL")
            #request.set("periodicitySelection", "MONTHLY")

            # append securities to request
            for isin in isins:
                request.append("securities", str(isin))

            # append fields to request
            for field in fields:
                request.append("fields", str(field))

            request.set("startDate", start_date.strftime('%Y%m%d'))
            request.set("endDate", end_date.strftime('%Y%m%d') if end_date is not None else start_date.strftime('%Y%m%d'))

            session.sendRequest(request)

            # Process received events
            try:
                dic = {}
                while (True):
                    # We provide timeout to give the chance to Ctrl+C handling:
                    ev = session.nextEvent(500)
                    if ev.eventType() == ev.RESPONSE or ev.eventType() == ev.PARTIAL_RESPONSE:
                        for msg in ev:
                            self._handle_error(msg)
                            secData = msg.getElement("securityData")
                            security = secData.getElement("security").getValue()
                            if not security in dic:
                                dic[security] = {}

                            for fieldData in secData.getElement("fieldData").values():
                                tick = {}
                                for field in fields:
                                    if fieldData.hasElement(field):
                                        tick[field] = fieldData.getElement(field).getValue()
                                dic[security][fieldData.getElement("date").getValue()] = tick

                    # Response completly received, so we could exit
                    if ev.eventType() == blpapi.Event.RESPONSE:
                        break

                return dic

            finally:
                # Stop the session
                session.stop()


    def BDP(self, isins, fields, overrides=[]):
        session = self._start_session()
        if session:
            if len(isins) == 0:
                print("No securities attached.")
                return

            if len(fields) == 0:
                print("No fields included.")
                return

            if not session.openService("//blp/refdata"):
                print("Failed to open //blp/refdata")
                return

            refDataService = session.getService("//blp/refdata")
            request = refDataService.createRequest("ReferenceDataRequest")

            # append securities to request
            for isin in isins:
                request.append("securities", str(isin))

            # append fields to request
            for field in fields:
                request.append("fields", str(field))

            # add overrides
            if len(overrides) > 0:
                req_overrides = request.getElement("overrides")
                elements = []
                for index, override in enumerate(overrides):
                    elements.append(req_overrides.appendElement())
                    elements[index].setElement("fieldId", override['field'])
                    elements[index].setElement("value", override['value'])

            session.sendRequest(request)

            try:
                dic = {}
                # Process received events
                while(True):
                    # We provide timeout to give the chance to Ctrl+C handling:
                    ev = session.nextEvent(500)
                    if ev.eventType() == ev.RESPONSE or ev.eventType() == ev.PARTIAL_RESPONSE:
                        for msg in ev:
                            self._handle_error(msg)
                            for secData in msg.getElement("securityData").values():
                                security = secData.getElement("security").getValue()
                                dic[security] = {}
                                for field in fields:
                                    if secData.getElement("fieldData").hasElement(field):
                                        dic[security][field] = secData.getElement("fieldData").getElement(field).getValue()
                    # Response completly received, so we could exit
                    if ev.eventType() == blpapi.Event.RESPONSE:
                        break

                return dic
            except DataQuotaLimitError as err:
                print("Bloomberg Error :", err)
                raise
            finally:
                # Stop the session
                session.stop()


if __name__ == '__main__':
    import datetime

    bloom = Bloomberg()
    #print(bloom.BDP(['IT0005415291@MILA Corp'], ['EQY_WEIGHTED_AVG_PX'], [{'field': 'VWAP_START_TIME', 'value': '10:30'}, {'field': 'VWAP_END_TIME', 'value': '15:30'}]))
    print(bloom.BDH(['IT0005415291@MILA Corp', 'IKA Comdty'], ['EQY_WEIGHTED_AVG_PX'], datetime.datetime(2020, 11, 30), datetime.datetime(2020, 12, 2)))



cdef extern from "Windows.h":
    cdef int CP_UTF8
    ctypedef unsigned short WORD
    ctypedef unsigned long DWORD
    ctypedef unsigned long *PDWORD
    ctypedef int BOOL
    ctypedef void *PVOID
    ctypedef PVOID HANDLE
    ctypedef PVOID *PHANDLE
    ctypedef unsigned long ULONG
    ctypedef ULONG *PULONG


cdef extern from "pwrdaq.h":
    enum _PD_SUBSYSTEM:
        pass
    ctypedef _PD_SUBSYSTEM PD_SUBSYSTEM

    struct _PD_DAQBUF_STATUS_INFO:
        pass
    ctypedef _PD_DAQBUF_STATUS_INFO *PPD_DAQBUF_STATUS_INFO

    struct _PD_AWFDESC:
        pass
    ctypedef _PD_AWFDESC *pPD_AWFDESC







# This command includes just before the include "pwrdaq32.h" the file
# redef_callback.h which contains redefinition of the preprocessing
# variable CALLBACK.
cdef extern from "redef_callback.h": 
     pass




cdef extern from "pwrdaq32.h":
    ctypedef void (__stdcall *PCALLBACK_FUNCTION) (PVOID pNormalContext, DWORD dwEvent, PVOID pCallbackContext)

    BOOL PdDriverOpen(PHANDLE phDriver, PDWORD pError, PDWORD pNumAdapters)
    BOOL PdDriverClose(HANDLE hDriver, PDWORD pError)

    BOOL _PdAdapterOpen(DWORD dwAdapter, PDWORD pError, PHANDLE phAdapter)
    BOOL _PdAdapterClose(HANDLE hAdapter, PDWORD pError)

    BOOL _PdAdapterEnableInterrupt(HANDLE hAdapter, DWORD *pError, DWORD dwEnable)

    BOOL PdAdapterAcquireSubsystem(HANDLE hAdapter, DWORD *pError,
                                   DWORD dwSubsystem, DWORD dwAcquire)


    # AIn Subsystem Commands:
    BOOL _PdAInSetCfg(HANDLE hAdapter, DWORD *pError, DWORD dwAInCfg,
                      DWORD dwAInPreTrig, DWORD dwAInPostTrig)
    BOOL _PdAInSetCvClk(HANDLE hAdapter, DWORD *pError, DWORD dwClkDiv)
    BOOL _PdAInSetClClk(HANDLE hAdapter, DWORD *pError, DWORD dwClkDiv)
    BOOL _PdAInSetChList(HANDLE hAdapter, DWORD *pError,
                         DWORD dwCh, DWORD *pdwChList)
    BOOL _PdAInGetStatus(HANDLE hAdapter, DWORD *pError, DWORD *pdwStatus)
    BOOL _PdAInEnableConv(HANDLE hAdapter, DWORD *pError, DWORD dwEnable)
    BOOL _PdAInSwStartTrig(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAInSwStopTrig(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAInSwCvStart(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAInSwClStart(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAInResetCl(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAInClearData(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAInReset(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAInGetValue(HANDLE hAdapter, DWORD *pError, WORD *pwSample)
    BOOL _PdAInGetSamples(HANDLE hAdapter, DWORD *pError,
                          DWORD dwMaxBufSize, WORD *pwBuf, DWORD *pdwSamples)
    BOOL _PdAInGetDataCount(HANDLE hAdapter, DWORD *pError, DWORD *pdwSamples)

    # AOut Subsystem Commands:
    BOOL _PdAOutSetCfg(HANDLE hAdapter, DWORD *pError,
                       DWORD dwAOutCfg, DWORD dwAOutPostTrig)
    BOOL _PdAOutSetCvClk(HANDLE hAdapter, DWORD *pError, DWORD dwClkDiv)

    BOOL _PdAOutGetStatus(HANDLE hAdapter, DWORD *pError, DWORD *pdwStatus)
    BOOL _PdAOutEnableConv(HANDLE hAdapter, DWORD *pError, DWORD dwEnable)
    BOOL _PdAOutSwStartTrig(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAOutSwStopTrig(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAOutSwCvStart(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAOutClearData(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAOutReset(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAOutPutValue(HANDLE hAdapter, DWORD *pError, DWORD dwValue)
    BOOL _PdAOutPutBlock(HANDLE hAdapter, DWORD *pError,
                         DWORD dwValues, DWORD *pdwBuf, DWORD *pdwCount)




    #
    # Asynchronous operations
    #
    # Subsystem-independent
    #
    #
    # Windows events
    BOOL _PdSetPrivateEvent(HANDLE hAdapter, HANDLE *phNotifyEvent)
    BOOL _PdClearPrivateEvent(HANDLE hAdapter, HANDLE *phNotifyEvent)
    
    BOOL _PdSetPrivateCallback(HANDLE hAdapter, PD_SUBSYSTEM Subsystem, 
                               PCALLBACK_FUNCTION pCallbackFunction,
                               PVOID pCallbackContext, HANDLE hThread) 
    BOOL _PdClearPrivateCallback(HANDLE hAdapter, PD_SUBSYSTEM Subsystem, 
                                 PCALLBACK_FUNCTION pCallbackFunction)

    # SDK events
    BOOL _PdSetUserEvents(HANDLE hAdapter, DWORD *pError,
                          PD_SUBSYSTEM Subsystem, DWORD dwEvents)
    BOOL _PdClearUserEvents(HANDLE hAdapter, DWORD *pError,
                            PD_SUBSYSTEM Subsystem, DWORD dwEvents)
    BOOL _PdGetUserEvents(HANDLE hAdapter, DWORD *pError,
                          PD_SUBSYSTEM Subsystem, DWORD *pdwEvents)
    BOOL _PdImmediateUpdate(HANDLE hAdapter, DWORD *pError)
    BOOL _PdWaitForEvent(HANDLE hAdapter, DWORD *pError, 
                         PD_SUBSYSTEM Subsystem, DWORD timeout, 
                         DWORD *pdwEvents)

    # Buffering
    BOOL _PdAcquireBuffer(HANDLE hAdapter, PDWORD pError,
                          void** pBuffer, DWORD dwFrames,
                          DWORD dwFrameScans, DWORD dwScanSamples,
                          DWORD dwSubsystem, DWORD dwMode)

    BOOL _PdReleaseBuffer(HANDLE hAdapter, PDWORD pError,
                          DWORD dwSubsystem, void* pBuffer)

    BOOL _PdGetDaqBufStatus(HANDLE hAdapter, DWORD *pError,
                            PPD_DAQBUF_STATUS_INFO pDaqBufStatus)

    BOOL _PdClearDaqBuf(HANDLE hAdapter, DWORD *pError,
                        PD_SUBSYSTEM Subsystem)
    
    BOOL _PdAInGetScans(HANDLE hAdapter, DWORD *pError,
                        DWORD NumScans, DWORD *pScanIndex,
                        DWORD *pNumValidScans)


    # Start input and output subsystem simultaneously
    BOOL _PdSyncStart(HANDLE hAdapter, PDWORD pError, DWORD dwSubsystem)


    # Analog Input
    BOOL _PdAInAsyncInit(HANDLE hAdapter, DWORD *pError,
                         ULONG dwAInCfg,
                         ULONG dwAInPreTrigCount, ULONG dwAInPostTrigCount,
                         ULONG dwAInCvClkDiv, ULONG dwAInClClkDiv,
                         ULONG dwEventsNotify,
                         ULONG dwChListChan, PULONG pdwChList)
    BOOL _PdAInAsyncTerm(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAInAsyncStart(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAInAsyncStop(HANDLE hAdapter, DWORD *pError)
    BOOL _PdAInGetBufState(HANDLE hAdapter, DWORD *pError,
                           DWORD NumScans, DWORD *pScanIndex,
                           DWORD *pNumValidScans)
    BOOL _PdAInSetPrivateEvent(HANDLE hAdapter, HANDLE *phNotifyEvent)
    BOOL _PdAInClearPrivateEvent(HANDLE hAdapter, HANDLE *phNotifyEvent)

    # Analog output
    #
    BOOL _PdAOutAsyncInit(HANDLE hAdapter, PDWORD pError, 
                          DWORD dwAOutCfg, DWORD dwAOutCvClkDiv, 
                          DWORD dwEventNotify)
    BOOL _PdAOutAsyncTerm(HANDLE hAdapter, PDWORD pError)
    BOOL _PdAOutAsyncStart(HANDLE hAdapter, PDWORD pError)
    BOOL _PdAOutAsyncStop(HANDLE hAdapter, PDWORD pError)
    BOOL _PdAOutGetBufState(HANDLE hAdapter, PDWORD pError,
                            DWORD NumScans, DWORD* pScanIndex,
                            DWORD* pNumValidScans)
    BOOL _PdAOutSetPrivateEvent(HANDLE hAdapter, HANDLE *phNotifyEvent)
    BOOL _PdAOutClearPrivateEvent(HANDLE hAdapter, HANDLE *phNotifyEvent)
    BOOL _PdAOutSetWave(HANDLE hAdapter, DWORD *pError,
                        DWORD dwCh, pPD_AWFDESC pdwData)
    BOOL _PdAOutProgramWave(HANDLE hAdapter, DWORD *pError,
                            DWORD dwOffset, DWORD dwSize, DWORD* pdwData)


    #==================================================================
    # 
    # Function convers raw values to volts
    #
    BOOL PdAInRawToVolts( HANDLE hAdapter,
                          DWORD dwAInCfg,     # Mode used
                          WORD* wRawData,     # Raw data
                          double* fVoltage,   # Engineering unit
                          DWORD dwCount       # Number of samples to convert
    )

    #==================================================================
    # 
    # Function convers raw values to volts
    #
    BOOL PdAOutVoltsToRaw( HANDLE hAdapter,
                           DWORD dwAOutCfg,   # Mode used
                           double* fVoltage,  # Engineering unit
                           DWORD* wRawData,   # Raw data
                           DWORD dwCount      # Number of samples to convert
    )


    # DIn Subsystem Commands:
    BOOL _PdDInSetCfg(HANDLE hAdapter, DWORD *pError, DWORD dwDInCfg)
    BOOL _PdDInGetStatus(HANDLE hAdapter, DWORD *pError, DWORD *pdwEvents)
    BOOL _PdDInRead(HANDLE hAdapter, DWORD *pError, DWORD *pdwValue)
    BOOL _PdDInClearData(HANDLE hAdapter, DWORD *pError)
    BOOL _PdDInReset(HANDLE hAdapter, DWORD *pError)
    BOOL _PdDInSetPrivateEvent(HANDLE hAdapter, HANDLE *phNotifyEvent)
    BOOL _PdDInClearPrivateEvent(HANDLE hAdapter, HANDLE *phNotifyEvent)

    # DOut Subsystem Commands:
    BOOL _PdDOutWrite(HANDLE hAdapter, DWORD *pError, DWORD dwValue)
    BOOL _PdDOutReset(HANDLE hAdapter, DWORD *pError)

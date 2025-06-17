/*
    Sample YARA rules for Sentinair
    Add your custom rules here
*/

rule SuspiciousExecutable
{
    meta:
        description = "Detects suspicious executable patterns"
        author = "Sentinair"
        date = "2024-01-01"
        
    strings:
        $hex1 = { 4D 5A 90 00 03 00 00 00 }
        $text1 = "CreateRemoteThread"
        $text2 = "VirtualAllocEx"
        $text3 = "WriteProcessMemory"
        
    condition:
        $hex1 at 0 and 2 of ($text*)
}

rule NetworkActivity
{
    meta:
        description = "Detects potential network activity in air-gapped system"
        
    strings:
        $net1 = "socket"
        $net2 = "connect"
        $net3 = "send"
        $net4 = "recv"
        
    condition:
        3 of them
}

rule SuspiciousUSBActivity
{
    meta:
        description = "Detects suspicious USB-related activity"
        
    strings:
        $usb1 = "USBSTOR"
        $usb2 = "RemovableMedia"
        $usb3 = "VID_"
        $usb4 = "PID_"
        
    condition:
        2 of them
}

rule DataExfiltration
{
    meta:
        description = "Detects potential data exfiltration patterns"
        
    strings:
        $file1 = ".zip"
        $file2 = ".rar"
        $file3 = ".7z"
        $cmd1 = "copy"
        $cmd2 = "xcopy"
        $cmd3 = "robocopy"
        
    condition:
        1 of ($file*) and 1 of ($cmd*)
}

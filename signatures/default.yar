
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

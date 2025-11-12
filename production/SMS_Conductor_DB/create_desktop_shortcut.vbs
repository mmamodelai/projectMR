Set oWS = WScript.CreateObject("WScript.Shell")
sDesktop = oWS.SpecialFolders("Desktop")

Set oLink = oWS.CreateShortcut(sDesktop & "\⚡ Restart Conductor.lnk")

' Get the current script directory
Set fso = CreateObject("Scripting.FileSystemObject")
sScriptPath = fso.GetParentFolderName(WScript.ScriptFullName)

oLink.TargetPath = sScriptPath & "\🔄 RESTART CONDUCTOR.bat"
oLink.WorkingDirectory = sScriptPath
oLink.Description = "Restart Conductor SMS System"
oLink.IconLocation = "C:\Windows\System32\imageres.dll,1" ' Exclamation/Warning icon (visible)
oLink.WindowStyle = 1 ' Normal window
oLink.Save

WScript.Echo "✅ Shortcut created on Desktop: ⚡ Restart Conductor"


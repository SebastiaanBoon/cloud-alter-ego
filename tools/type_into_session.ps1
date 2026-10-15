# Types text into the console of a running Claude session on this PC (hidden PowerShell windows), for example
# /rename. Send the command in chunks with a pause: "/rename", " ", each word, then [char]13 (Enter).
# Usage: powershell -File tools\type_into_session.ps1 -ProcessId <claude.exe pid> -Text '/rename'
param([int]$ProcessId, [string]$Text)
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class ConIn3 {
    [StructLayout(LayoutKind.Explicit, CharSet = CharSet.Unicode)]
    public struct KEY_EVENT_RECORD {
        [FieldOffset(0)] public int bKeyDown;
        [FieldOffset(4)] public short wRepeatCount;
        [FieldOffset(6)] public short wVirtualKeyCode;
        [FieldOffset(8)] public short wVirtualScanCode;
        [FieldOffset(10)] public char UnicodeChar;
        [FieldOffset(12)] public int dwControlKeyState;
    }
    [StructLayout(LayoutKind.Explicit)]
    public struct INPUT_RECORD {
        [FieldOffset(0)] public short EventType;
        [FieldOffset(4)] public KEY_EVENT_RECORD KeyEvent;
    }
    [DllImport("kernel32.dll", SetLastError = true)] public static extern bool FreeConsole();
    [DllImport("kernel32.dll", SetLastError = true)] public static extern bool AttachConsole(int pid);
    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    public static extern IntPtr CreateFile(string name, uint access, uint share, IntPtr sec, uint disp, uint flags, IntPtr tmpl);
    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    public static extern bool WriteConsoleInput(IntPtr h, INPUT_RECORD[] buf, int len, out int written);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern short VkKeyScan(char ch);
    [DllImport("user32.dll")] public static extern uint MapVirtualKey(uint code, uint mapType);
    public static string Type(int pid, string text) {
        FreeConsole();
        if (!AttachConsole(pid)) return "attach failed " + Marshal.GetLastWin32Error();
        IntPtr h = CreateFile("CONIN$", 0xC0000000, 3, IntPtr.Zero, 3, 0, IntPtr.Zero);
        var recs = new System.Collections.Generic.List<INPUT_RECORD>();
        foreach (char c in text) {
            short scan = VkKeyScan(c);
            short vk = (short)(scan & 0xFF);
            bool shift = (scan & 0x100) != 0;
            if (c == '\r') { vk = 0x0D; shift = false; }
            short sc = (short)MapVirtualKey((uint)vk, 0);
            foreach (int down in new[] {1, 0}) {
                var r = new INPUT_RECORD(); r.EventType = 1;
                r.KeyEvent.bKeyDown = down; r.KeyEvent.wRepeatCount = 1;
                r.KeyEvent.UnicodeChar = c; r.KeyEvent.wVirtualKeyCode = vk; r.KeyEvent.wVirtualScanCode = sc;
                r.KeyEvent.dwControlKeyState = shift ? 0x10 : 0;
                recs.Add(r);
            }
        }
        int w; bool ok = WriteConsoleInput(h, recs.ToArray(), recs.Count, out w);
        FreeConsole();
        return ok ? ("written " + w) : ("write failed " + Marshal.GetLastWin32Error());
    }
}
"@
[ConIn3]::Type($ProcessId, $Text)

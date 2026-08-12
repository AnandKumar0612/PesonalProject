import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading

try:
    from ppadb.client import Client as AdbClient
except ImportError:
    AdbClient = None

# ── Device registry ──────────────────────────────────────────────────────────
USER_DATA = {
    "TCL TV Home":    "192.168.0.160",
    "Fire Cube":      "10.1.92.58",
    "Mi TV":          "10.1.92.59",
    "Chromecast":     "10.1.92.60",
    "Fire TV":        "10.1.92.61",
    "TCL TV":         "10.1.92.46",
    "Philips TV":     "10.1.92.36",
    "Panasonic TV":   "10.1.92.35",
    "Sony TV ME":     "10.1.92.34",
    "Grundig TV":     "10.1.92.41",
    "Telefunken TV":  "10.1.92.44",
    "Sony TV HE":     "10.1.92.74",
}

# ── Palette ──────────────────────────────────────────────────────────────────
BG       = "#0d0f14"
SURFACE  = "#161a23"
CARD     = "#1e2433"
BORDER   = "#2a3045"
ACCENT   = "#00c8ff"
ACCENT2  = "#0078d4"
SUCCESS  = "#00e676"
WARNING  = "#ffab00"
ERROR    = "#ff5252"
TEXT     = "#e8eaf0"
SUBTEXT  = "#7a8299"
MONO     = ("Consolas", 9)
UI       = ("Segoe UI", 10)
HEAD     = ("Segoe UI Semibold", 11)
BIG      = ("Segoe UI Light", 22)


class TextSenderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart TV · ADB Text Sender")
        self.geometry("620x580")
        self.minsize(540, 500)
        self.configure(bg=BG)
        self.resizable(True, True)

        self._client = None
        self._connected_ip = None

        self._build_ui()
        self._run(self._start_daemon)

    # ── UI ───────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="⌨  ADB Text Sender", font=BIG, bg=BG, fg=TEXT).pack(side="left")
        self._dot = tk.Label(hdr, text="●", font=("Segoe UI", 14), bg=BG, fg=SUBTEXT)
        self._dot.pack(side="right", padx=(0, 4))
        self._status_lbl = tk.Label(hdr, text="Initialising…", font=UI, bg=BG, fg=SUBTEXT)
        self._status_lbl.pack(side="right")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=24, pady=12)

        # ── Device card ──
        dev_card = self._card("Device Selection")

        tk.Label(dev_card, text="Select Device", font=UI, bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(0, 4))

        dd_row = tk.Frame(dev_card, bg=CARD)
        dd_row.pack(fill="x", pady=(0, 8))
        dd_row.columnconfigure(0, weight=1)

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Dark.TCombobox",
                        fieldbackground=SURFACE, background=SURFACE,
                        foreground=TEXT, arrowcolor=ACCENT,
                        selectbackground=ACCENT2, selectforeground=TEXT,
                        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
        style.map("Dark.TCombobox",
                  fieldbackground=[("readonly", SURFACE)],
                  foreground=[("readonly", TEXT)])

        self._device_var = tk.StringVar()
        self._dropdown = ttk.Combobox(
            dd_row, textvariable=self._device_var,
            values=list(USER_DATA.keys()),
            state="readonly", style="Dark.TCombobox",
            font=UI
        )
        self._dropdown.grid(row=0, column=0, sticky="ew", ipady=5, padx=(0, 8))
        self._dropdown.set(list(USER_DATA.keys())[0])
        self._dropdown.bind("<<ComboboxSelected>>", self._on_device_change)

        # IP preview label
        self._ip_lbl = tk.Label(dd_row, text=list(USER_DATA.values())[0],
                                font=MONO, bg=SURFACE, fg=ACCENT,
                                padx=10, pady=6, relief="flat",
                                highlightthickness=1, highlightbackground=BORDER)
        self._ip_lbl.grid(row=0, column=1)

        # Connect / Disconnect buttons
        btn_row = tk.Frame(dev_card, bg=CARD)
        btn_row.pack(fill="x", pady=(4, 0))
        self._btn_connect = self._btn(btn_row, "Connect", self._on_connect, ACCENT2)
        self._btn_connect.pack(side="left", padx=(0, 8))
        self._btn_disconnect = self._btn(btn_row, "Disconnect", self._on_disconnect, SURFACE)
        self._btn_disconnect.pack(side="left")
        self._conn_badge = tk.Label(btn_row, text="", font=UI, bg=CARD, fg=SUCCESS)
        self._conn_badge.pack(side="left", padx=12)

        # ── Text card ──
        txt_card = self._card("Send Text")

        tk.Label(txt_card, text="Text to Send", font=UI, bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(0, 4))

        self._text_var = tk.StringVar()
        txt_entry = tk.Entry(txt_card, textvariable=self._text_var,
                             font=("Consolas", 12),
                             bg=SURFACE, fg=TEXT, insertbackground=ACCENT,
                             relief="flat", highlightthickness=1,
                             highlightbackground=BORDER, highlightcolor=ACCENT)
        txt_entry.pack(fill="x", ipady=8, pady=(0, 12))
        txt_entry.bind("<Return>", lambda e: self._on_send())

        self._btn_send = self._btn(txt_card, "  ▶  Send Text  ", self._on_send,
                                   ACCENT2, font=("Segoe UI Semibold", 11))
        self._btn_send.pack(fill="x", ipady=8)

        # Progress bar
        style.configure("Accent.Horizontal.TProgressbar",
                        troughcolor=SURFACE, background=ACCENT,
                        darkcolor=ACCENT, lightcolor=ACCENT, bordercolor=CARD)
        self._progress = ttk.Progressbar(txt_card,
                                          style="Accent.Horizontal.TProgressbar",
                                          mode="indeterminate")
        self._progress.pack(fill="x", pady=(8, 0))

        # ── Log ──
        self._build_log()

    def _card(self, title):
        outer = tk.Frame(self, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        outer.pack(fill="x", padx=24, pady=(0, 12))
        hdr = tk.Frame(outer, bg=CARD)
        hdr.pack(fill="x", padx=14, pady=(10, 6))
        tk.Label(hdr, text=title, font=HEAD, bg=CARD, fg=ACCENT).pack(side="left")
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", padx=14)
        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill="both", expand=True, padx=14, pady=10)
        return inner

    def _build_log(self):
        log_outer = tk.Frame(self, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        log_outer.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        hdr = tk.Frame(log_outer, bg=CARD)
        hdr.pack(fill="x", padx=14, pady=(8, 4))
        tk.Label(hdr, text="Output Log", font=HEAD, bg=CARD, fg=ACCENT).pack(side="left")
        self._btn(hdr, "Clear", self._clear_log, SURFACE).pack(side="right")
        tk.Frame(log_outer, bg=BORDER, height=1).pack(fill="x", padx=14)
        self._log = scrolledtext.ScrolledText(
            log_outer, bg=SURFACE, fg=TEXT, font=MONO,
            relief="flat", state="disabled", wrap="word", padx=8, pady=6, height=7
        )
        self._log.pack(fill="both", expand=True, padx=8, pady=8)
        self._log.tag_config("ok",   foreground=SUCCESS)
        self._log.tag_config("err",  foreground=ERROR)
        self._log.tag_config("warn", foreground=WARNING)
        self._log.tag_config("info", foreground=ACCENT)
        self._log.tag_config("dim",  foreground=SUBTEXT)

    def _btn(self, parent, text, cmd, bg, font=UI):
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, fg=TEXT, activebackground=ACCENT2,
                         activeforeground=TEXT, font=font,
                         relief="flat", cursor="hand2", padx=12, pady=4, bd=0)

    # ── Logging helpers ───────────────────────────────────────────────────────
    def _write(self, msg, tag=""):
        def _do():
            self._log.config(state="normal")
            self._log.insert("end", msg + "\n", tag)
            self._log.see("end")
            self._log.config(state="disabled")
        self.after(0, _do)

    def ok(self, m):   self._write(f"✔  {m}", "ok")
    def err(self, m):  self._write(f"✖  {m}", "err")
    def warn(self, m): self._write(f"⚠  {m}", "warn")
    def info(self, m): self._write(f"›  {m}", "info")
    def dim(self, m):  self._write(f"   {m}", "dim")

    def _set_status(self, text, colour):
        self.after(0, lambda: (
            self._status_lbl.config(text=text, fg=colour),
            self._dot.config(fg=colour)
        ))

    def _clear_log(self):
        self._log.config(state="normal")
        self._log.delete("1.0", "end")
        self._log.config(state="disabled")

    def _busy(self, on):
        self.after(0, lambda: (
            self._progress.start(12) if on else self._progress.stop(),
            self._btn_send.config(state="disabled" if on else "normal")
        ))

    def _run(self, fn, *args):
        threading.Thread(target=fn, args=args, daemon=True).start()

    # ── Event handlers ────────────────────────────────────────────────────────
    def _on_device_change(self, _event=None):
        name = self._device_var.get()
        ip = USER_DATA.get(name, "")
        self._ip_lbl.config(text=ip)
        # reset connection badge if device changes
        if self._connected_ip and self._connected_ip != ip:
            self.after(0, lambda: self._conn_badge.config(text=""))

    def _on_connect(self):
        name = self._device_var.get()
        ip = USER_DATA.get(name)
        if not ip:
            messagebox.showwarning("No Device", "Select a device first.")
            return
        self._run(self._connect_device, ip, name)

    def _connect_device(self, ip, name):
        self.info(f"Connecting to {name} ({ip}:5555) …")
        if not self._client:
            self._init_client()
            if not self._client:
                return
        try:
            self._client.remote_connect(ip, 5555)
            devices = self._client.devices()
            if devices:
                self._connected_ip = ip
                self.ok(f"Connected: {devices[0].serial}")
                self._set_status(f"Connected · {name}", SUCCESS)
                self.after(0, lambda: self._conn_badge.config(
                    text=f"● Connected", fg=SUCCESS))
            else:
                self.err("Connected but no device visible. Check ADB/TV settings.")
        except Exception as e:
            self.err(f"Connection failed: {e}")

    def _on_disconnect(self):
        ip = self._connected_ip or USER_DATA.get(self._device_var.get())
        if not ip:
            messagebox.showinfo("Not Connected", "No active connection to disconnect.")
            return
        self._run(self._disconnect_device, ip)

    def _disconnect_device(self, ip):
        self.info(f"Disconnecting {ip} …")
        try:
            if self._client:
                self._client.remote_disconnect(ip)
            subprocess.run(["adb", "kill-server"], capture_output=True, text=True)
            self._connected_ip = None
            self._client = None
            self.ok("Disconnected. ADB server stopped.")
            self._set_status("Disconnected", WARNING)
            self.after(0, lambda: self._conn_badge.config(text=""))
        except Exception as e:
            self.err(f"Disconnect error: {e}")

    def _on_send(self):
        name = self._device_var.get()
        ip   = USER_DATA.get(name)
        text = self._text_var.get().strip()

        if not name:
            messagebox.showwarning("No Device", "Select a device.")
            return
        if not text:
            messagebox.showwarning("No Text", "Enter text to send.")
            return
        self._run(self._send_flow, ip, name, text)

    def _send_flow(self, ip, name, text):
        self._busy(True)
        try:
            if not self._client:
                self._init_client()
                if not self._client:
                    return

            self.info(f"Connecting to {name} ({ip}) …")
            self._client.remote_connect(ip, 5555)
            devices = self._client.devices()

            if not devices:
                self.err("No devices found. Ensure ADB debugging is enabled on TV.")
                return

            device = devices[0]
            self._connected_ip = ip
            self.dim(f"Device serial: {device.serial}")
            self.after(0, lambda: self._conn_badge.config(text="● Connected", fg=SUCCESS))

            self.info(f'Sending text: "{text}"')
            output = device.shell(f'input text "{text}" && echo "success"')

            if "success" in output:
                self.ok(f'Text sent successfully → "{text}"')
                self._set_status("Text sent ✓", SUCCESS)
            else:
                self.err(f"Send failed. Device output: {output.strip() or '(empty)'}")
                self._set_status("Send failed", ERROR)

        except Exception as e:
            self.err(f"Error: {e}")
            self._set_status("Error", ERROR)
        finally:
            self._busy(False)

    # ── ADB internals ─────────────────────────────────────────────────────────
    def _start_daemon(self):
        self.info("Starting ADB daemon…")
        try:
            subprocess.run(["adb", "start-server"], check=True,
                           capture_output=True, text=True)
            self.ok("ADB daemon started.")
            self._set_status("ADB ready", SUCCESS)
            self._init_client()
        except FileNotFoundError:
            self.err("'adb' not found — add Android platform-tools to PATH.")
            self._set_status("ADB missing", ERROR)
        except subprocess.CalledProcessError as e:
            self.err(f"Daemon error: {e.stderr.strip()}")
            self._set_status("Daemon error", ERROR)

    def _init_client(self):
        if AdbClient is None:
            self.err("ppadb not installed. Run: pip install pure-python-adb")
            return
        try:
            self._client = AdbClient(host="127.0.0.1", port=5037)
        except Exception as e:
            self.err(f"ADB client init failed: {e}")


if __name__ == "__main__":
    app = TextSenderApp()
    app.mainloop()

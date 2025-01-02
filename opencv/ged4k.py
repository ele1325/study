#  Copyright (c) 2024 AOX Technologies GmbH, Germany

import hashlib
import json
import os
import re
import requests
import requests_toolbelt
import socket
import threading
import time
from typing import Optional


class GED4KError(Exception):
    def __init__(self, message):
        super().__init__(f"GED4K: {message}")


class GED4KRpcError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class Display():
    def __init__(self, slot, lane, repeater):
        """
        @brief Class Display constructor

        @param slot: RX/TX module slot (int)
        @param lane: APIX lane the receiver is connected to (int)
        @param repeater: Receiver APIX repeater number (int)
        """

        super().__init__()

        self.__slot = slot
        self.__lane = lane
        self.__repeater = repeater

    def get_slot(self):
        return self.__slot

    def get_lane(self):
        return self.__lane

    def get_repeater(self):
        return self.__repeater


class GED4KControl():
    def __init__(self, ip_addr: str, rpc_port: int = 55555,
                 http_port: int = 80):
        """
        @brief Class GED4KControl constructor

        @param ip_addr GED4K IP address
        @param rpc_port GED4K RPC port. Defaults to 55555 if not specified.
        @param http_port GED4K HTTP port. Defaults to 80 if not specified.
        """

        super().__init__()

        self.__ip_addr = ip_addr
        self.__rpc_port = rpc_port
        self.__http_port = http_port
        self.__diag_job_finished_callbacks = []
        self.__flashing_progress_callbacks = []
        self.__flashing_finished_callbacks = []
        self.__file_upload_progress_callbacks = []
        self.__counter = 0
        self.__expert_mode = False

        self.config = {'fw_flashing': {'initial_reset': True,
                                       'flash_mode_confirm_timeout': 30,
                                       'chunk_transfer_timeout': 30,
                                       'memory_check_timeout': 30,
                                       'fw_activation_timeout': 180,
                                       'commit_changes_timeout': 30,
                                       'shutdown_timeout': 30,
                                       'timeout': 30},
                       'fw_flashing_test': {'test': None},
                       'lifecycle': {'shutdown_timeout': 10},
                       'diagnostics': {'timeout': 10}}

    # Internal Methods
    def __get_display_name(self, slot, lane, repeater):
        return "%s:%s.%s" % (slot, lane, repeater)

    def _run_flashing_progress_callbacks(self, *args, **kwargs):
        for callback in self.__flashing_progress_callbacks:
            callback(*args, **kwargs)

    def _run_flashing_finished_callbacks(self, *args, **kwargs):
        for callback in self.__flashing_finished_callbacks:
            callback(*args, **kwargs)

    def __run_file_upload_progress_callbacks(self, *args, **kwargs):
        for callback in self.__file_upload_progress_callbacks:
            callback(*args, **kwargs)

    def __start_diag_job(self, **params):
        self.diag_thread = threading.Thread(target=self.__diag_thread_worker,
                                            kwargs=params)

        self.diag_thread.start()

    def __diag_thread_worker(self, **params):
        worker = self.DiagWorker(self, **params)
        worker.worker_finished_callback = self.__stop_diag_job
        worker.do_work()

    def __stop_diag_job(self, result):
        self.__run_diag_callbacks(result)

    def __run_diag_callbacks(self, *args, **kwargs):
        for callback in self.__diag_job_finished_callbacks:
            callback(*args, **kwargs)

    def _rpc(self, method: str, rpc_timeout: float, **params):
        """
        Sends a JSON-RPC request to the object

        @param method The name of the RPC method to call.
        @param rpc_timeout The maximum time (in seconds) to wait for a response
               from the RPC server.
        @param params A variable-length dictionary of additional parameters to
               include in the RPC call.

        @return The result of the RPC call, or None if no response was received
                within the timeout period.
        """

        now = time.monotonic()
        deadline = now + rpc_timeout

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(deadline - now)
        sock.connect((self.__ip_addr, self.__rpc_port))

        self.__counter += 1
        msg = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": self.__counter,
        }

        msg = bytes(json.dumps(msg), encoding='utf-8')
        sock.sendall(msg)

        buf = bytearray(1024 * 1024)
        bufview = memoryview(buf)
        idx = 0
        now = time.monotonic()

        while deadline > now:
            try:
                sock.settimeout(deadline - now)
                idx += sock.recv_into(bufview[idx:])
                obj = json.loads(buf[:idx])
                return obj
            except Exception as e:
                now = time.monotonic()

        raise TimeoutError("RPC Timeout")

    def __file_upload(self, filepath, targetname, progress=False):
        def report_progress(monitor):
            self.__run_file_upload_progress_callbacks(monitor.bytes_read / self.total_size * 100)

        url = "http://%s:%d/cgi-bin/fileupload.cgi" % (self.__ip_addr,
                                                       self.__http_port)
        response = None
        proxies = {"http": None}
        try:
            if progress:
                with open(filepath, "rb") as file:
                    self.total_size = os.path.getsize(filepath)

                    e = requests_toolbelt.MultipartEncoder(fields={'file': (targetname, file)})
                    m = requests_toolbelt.MultipartEncoderMonitor(e, report_progress)
                    response = requests.post(url,
                                             data=m,
                                             headers={'Content-Type': m.content_type},
                                             proxies=proxies)

            else:
                with open(filepath, "rb") as file:
                    response = requests.post(url,
                                             files={'file': (targetname, file)},
                                             proxies=proxies)

        except Exception as e:
            raise Exception("File upload failed: " + str(e))

        info = ""
        if response.status_code != 200:
            raise GED4KRpcError(str(response.status_code),
                                str(response.content))
        else:
            info = json.loads(response.content)

        return info

    # Public API ###########################################################

    def set_expert_mode(self, mode):
        """
        @brief Enables or disables expert mode

        @param mode: True or False (bool)
        """
        self.__expert_mode = mode

    def get_expert_mode(self):
        """
        @brief Returns if expert mode is enabled or not

        @return: True if expert mode is enabled, False if not.
        """
        return self.__expert_mode

    def register_callback_diag_job_finished(self, callback):
        """
        @brief Register a callback for diagnotic job results

        @param callback Function that shall be called after
                        the diagnostic job has finished
        """
        self.__diag_job_finished_callbacks.append(callback)

    def unregister_callback_diag_job_finished(self, callback):
        """
        @brief Unregister a callback for diagnostic job results

        @param callback Function to get unregistered
        """
        if callback in self.__diag_job_finished_callbacks:
            self.__diag_job_finished_callbacks.remove(callback)

    def register_callback_flashing_finished(self, callback):
        """
        @brief Register a callback for flashing results

        @param callback Function that shall be called after
                        flashing has finished
        """
        self.__flashing_finished_callbacks.append(callback)

    def unregister_callback_flashing_finished(self, callback):
        """
        @brief Unregister a callback for flashing results

        @param callback Function to get unregistered
        """
        if callback in self.__flashing_finished_callbacks:
            self.__flashing_finished_callbacks.remove(callback)

    def register_callback_flashing_progress(self, callback):
        """
        @brief Register a callback for flashing progress

        @param callback Function that shall be called to
                        report flashing progress
        """
        self.__flashing_progress_callbacks.append(callback)

    def unregister_callback_flashing_progress(self, callback):
        """
        @brief Unregister a callback for flashing progress

        @param callback Function to get unregistered
        """
        if callback in self.__flashing_progress_callbacks:
            self.__flashing_progress_callbacks.remove(callback)

    def register_callback_file_upload_progress(self, callback):
        """
        @brief Register a callback for file upload progress

        @param callback Function that shall be called
        """
        self.__file_upload_progress_callbacks.append(callback)

    def unregister_callback_file_upload_progress(self, callback):
        """
        @brief Unregister a callback for file upload progress

        @param callback Function to get unregistered
        """
        if callback in self.__file_upload_progress_callbacks:
            self.__file_upload_progress_callbacks.remove(callback)

    def get_link_state(self, display: Display):
        """
        @brief Returns the communication link state

        @param display: A Display instance

        @returns Link state (str)
        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs.
        """

        name = self.__get_display_name(display.get_slot(),
                                       display.get_lane(),
                                       display.get_repeater())
        params = {
            "state": "/displays/" + name + "/link"
        }

        try:
            response = self._rpc("get_state", 2.0, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
            if response["result"] is None:
                raise Exception(f"Unknown RPC Error")
            else:
                return response["result"]
        except Exception as e:
            raise GED4KError(f"{str(e)}")

    def get_sw_version(self):
        """
        @brief Returns the GED4K SW version as string

        @returns GED4K SW version (str)
        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs.
        """
        params = {
        }

        try:
            response = self._rpc("ged4k_sw_version", 2.0, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
            if response["result"] is None:
                raise Exception(f"Unknown RPC Error")
            else:
                return response["result"]
        except Exception as e:
            raise GED4KError(f"{str(e)}")

    def get_ip_addr(self):
        """
        @brief Get GED4K IP address

        @return GED4K IP address (str)
        """
        return self.__ip_addr

    def get_http_port(self):
        """
        @brief Get GED4K HTTP port

        @return GED4K HTTP port (int)
        """
        return self.__http_port

    def get_rpc_port(self):
        """
        @brief Get GED4K RPC port

        @return GED4K RPC port (int)
        """
        return self.__rpc_port

    def set_flashing_param(self, params: dict):
        """
        @brief Update flashing configuration parameters

        @param params Parameters to update (dict)
        """

        for i in ['fw_flashing', 'fw_flashing_test', 'lifecycle']:
            p = params.get(i)
            if p:
                for key, value in p.items():
                    self.config[i][key] = value

    def get_flashing_param(self, key):
        """
        @brief Get flashing configuration parameter value

        @param key: The key of the parameter to retrieve (str).
                    Keys are separated by dots.

        @return: The value of the parameter, or None if not found.
        """

        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k)
            if value is None:
                return None

        return value

    def start_flashing(self, display: Display, fw_filename_btld: str, fw_filename_swfl: str,
                       transfer_fw: bool = True, activate_fw: bool = True):
        """
        @brief Flash firmware

        @pre register_callback_flashing_finished must be called before in order
             to register a callback retrieving the final result
        @pre register_callback_flashing_progress must be called before in order
             to register a callback retrieving updates during flashing
        @post unregister_callback_flashing_finished shall be called after
              flashing has finished
        @post unregister_callback_flashing_progress shall be called after
              flashing has finished

        @param fw_btld The path to the BTLD file.
        @param fw_swfl The path to the SWFL file.
        @param activate_fw Whether or not to activate the firmware.
               Default is True.
        @param slot The daughter board slot number. Default is 3.
        @param lane The APIX lane number. Default is 0.
        @param repeater The APIX repeater number or None for all. Default is 0.
        """

        worker = self.FlashingWorker(self,
                                     self._run_flashing_progress_callbacks,
                                     self._run_flashing_finished_callbacks,
                                     fw_filename_btld, fw_filename_swfl,
                                     transfer_fw, activate_fw,
                                     display.get_slot(),
                                     display.get_lane(),
                                     display.get_repeater())
        self.flashing_thread = threading.Thread(target=worker.run)
        self.flashing_thread.start()

    def simulate_touch_events(self, display: Display, touch_events):
        """
        @brief Simulate touch events

        @param display: A Display instance
        @param touch_event: An array of tuples representing touch events.
                        Each tuple should have the following structure:
                        type: str, slot: int, x: int, y: int
                        (list[tuple[str, int, int, int]])

        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs
        """
        for event in touch_events:
            try:
                event_type = event["type"]
            except Exception as e:
                raise GED4KError(f"simulate_touch_events: {str(e)}")

            if (event_type == "TOUCH_EVENT_TOUCH_DOWN"):
                event["type"] = 1
            elif (event_type == "TOUCH_EVENT_DATA"):
                event["type"] = 2
            elif (event_type == "TOUCH_EVENT_LIFT_OFF"):
                event["type"] = 3
            else:
                raise GED4KError("simulate_touch_events: Invalid event type")

        params = {
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
            "touchEvents": touch_events
        }

        try:
            response = self._rpc(method="simulateTouchEvents", **params, rpc_timeout=5)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
            if response["result"] is None:
                return []
            else:
                return response["result"]
        except Exception as e:
            raise GED4KError(f"simulateTouchEvents: {str(e)}")

    def gdcn_send(self, display: Display,
                  channel: int, cmd_id: int, payload: tuple = None):
        """
        @brief Send a GDCN command to a given receiver

        @param display: A Display instance
        @param channel: GDCN channel number (int)
        @param cmd_id: GDCN command ID (int)
        @param payload: GDCN command payload (tuple)

        @returns GDCN message return value (array)
        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs
        """

        params = {
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
            "cmd_id": cmd_id,
            "channel": channel,
            "val": payload
        }

        try:
            response = self._rpc(method="gdcn_send", **params, rpc_timeout=5)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
            if response["result"] is None:
                return []
            else:
                return response["result"]
        except Exception as e:
            raise GED4KError(f"gdcn_send: {str(e)}")

    def oob_on(self, display: Display):
        """
        @brief Enable target by OOB line


        @param display: A Display instance
        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs.
        """

        params = {
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
            "val": 1,
        }

        try:
            response = self._rpc("oob_on_off", 2.0, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
        except Exception as e:
            raise GED4KError(f"{str(e)}")

    def oob_off(self, display: Display):
        """
        @brief Enable target by OOB line


        @param display: A Display instance
        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs.
        """

        params = {
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
            "val": 0
        }

        try:
            response = self._rpc("oob_on_off", 2.0, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
        except Exception as e:
            raise GED4KError(f"{str(e)}")

    def startup(self, display: Display):
        """
        @brief Wakeup target according to the specification

        @param display: A Display instance
        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs.
        """

        params = {
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
        }

        try:
            response = self._rpc("wakeup", 2.0, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
        except Exception as e:
            raise GED4KError(f"{str(e)}")

    def shutdown(self, display: Display):
        """
        @brief Shutdown target according to the specification

        @param display: A Display instance
        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs.
        """

        timeout = self.config['lifecycle']['shutdown_timeout']

        params = {
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
            "timeout": timeout
        }

        try:
            response = self._rpc("shutdown", timeout, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
        except Exception as e:
            raise GED4KError(f"{str(e)}")

    def suspend(self, display: Display,
                wake_on_touch_button: bool, wake_on_touch_display: bool):
        """
        @brief Suspend display and host

        Initiates sequence on host for suspending display with Wake-on-Touch
        and suspending host leaving OOB enabled.
        The host can be woken up by an OOB-ACK signal from the display.

        @param display: A Display instance
        """
        params = {
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
            "wake_on_touch": {
                "button": wake_on_touch_button,
                "display": wake_on_touch_display,
            }
        }

        try:
            response = self._rpc("suspend", 5, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
        except Exception as e:
            raise GED4KError(f"{str(e)}")

    def write_pia_data(self, pia_data: dict):
        """
        @brief Update PIA data stored on the host

        @param pia_data: PIA indices and corresponding values (dict)

        @returns Updated PIA data (dict)

        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs.
        """

        params = {
            "pia_data": pia_data
        }

        try:
            response = self._rpc("write_pia_data", rpc_timeout=2.0, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
        except Exception as e:
            raise GED4KError(f"{str(e)}")

        return response['result']['pia']

    def write_warping_set(self, filepath):
        """
        @brief Upload warping set to GED4K host

        @param filepath: Path to file that shall be uploaded

        @return info File information (dict)

        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs.
        """

        if not filepath:
            raise Exception("GED4K WriteWarpingSet:: No Warping Set")

        reg = r"^.+_OptVariant_(Left|Middle|Right)_(.+?_)?([0-9A-F]{16})\.bin$"
        pattern = re.compile(reg)
        filename = os.path.basename(filepath)
        match = re.match(pattern, filename)
        if not match:
            raise Exception("GED4K WriteWarpingSet: Invalid filename")

        url = "http://%s:%d/cgi-bin/warpingsetupload.cgi" % (self.__ip_addr,
                                                             self.__http_port)

        response = None
        proxies = {"http": None}
        local_hash = ""

        try:
            with open(filepath, "rb") as f:
                response = requests.post(url, files={'file': f},
                                         proxies=proxies)
                f.seek(0)
                data = f.read()
                local_hash = hashlib.md5(data).hexdigest()
        except Exception as e:
            raise Exception("GED4K WriteWarpingSet: open:" + str(e))

        info = ""
        try:
            info = json.loads(response.content)
            if info['status'] == 'success':
                if info['md5sum'] != local_hash:
                    raise Exception("GED4K WriteWarpingSet: Upload failed")
        except Exception as e:
            raise Exception("GED4K WriteWarpingSet: Invalid response" + str(e))

        return info

    def get_param(self, json_pointer):
        """
        @brief Get current target configuration

        @param json_pointer: The key to the json(config)-tree to print
                             (string). Root is "".
        @return All parameters which are referenced by the json_pointer.

        @raises GED4KError: If a JSON-RPC error or an unexpected error
                            occurs.
        """

        params = {
            "key": json_pointer
        }

        try:
            response = self._rpc(method="get_param", rpc_timeout=5, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
            if response["result"] is None:
                return []
            else:
                return response["result"]
        except Exception as e:
            raise GED4KError(f"{str(e)}")

    def set_param(self, json_pointer, value, write: bool = False):
        """
        @brief Update current target configuration.

        @param json_pointer: The key of the json(config)-tree to change
                             (string).
        @param value: The content for the update (correct type and format).
        @param write: The flag for using persistent config update (bool).

        @return Updated config tree (array)

        @raises GED4KError: If a JSON-RPC error or an unexpected error
                            occurs.
        """

        params = {
            "key": json_pointer,
            "val": value,
            "persist": write
        }

        try:
            response = self._rpc(method="set_param", rpc_timeout=5, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
            if response["result"] is None:
                return []
            else:
                return response["result"]
        except Exception as e:
            raise GED4KError(f"{str(e)}")

    def reset_param(self, exitcode: int = 117):
        """
        @brief Reset current target configuration to default.

        @param path: The path to the file to remove (string).
        @param exitcode: The exit code for the main app (int).

        @return Reply message and exit code

        @raises GED4KError: If a JSON-RPC error or an unexpected error
                            occurs.
        """

        params = {
            "code": exitcode
        }

        try:
            # Remove persistent config
            response_remove = self._rpc(method="remove_persistent_config",
                                        rpc_timeout=5)
            # Restart main application for reloading default config
            response_restart = self._rpc(method="restart_main_app",
                                         rpc_timeout=5, **params)
            if "error" in response_remove:
                raise Exception(f"{response_remove['error']['message']}")
            if "error" in response_restart:
                raise Exception(f"{response_restart['error']['message']}")
            else:
                return response_remove["result"]["message"],
            response_restart["result"]["code"]
        except Exception as e:
            raise GED4KError(f"{str(e)}")

    def get_state(self, json_pointer):
        """
        @brief Get current state of GED4k.

        This method allows to query certain runtime states of the GED4k.
        States are identfied by a JSON pointer. Multiple states can be queried
        by providing a JSON pointer to the common parent node for those states.

        For GED4k configured as host the following states are available:
        - /displays/<display>/link
        - /displays/<display>/state
        - /displays/<display>/startup_events
        - /displays/<display>/timings

        For GED4k configured as display the following states are available:
        - /displays/<display>/link
        - /displays/<display>/timings

        @param json_pointer: JSON pointer of state to return
        @return State as JSON value referenced by the json_pointer.

        @raises GED4KError: If a JSON-RPC error or an unexpected error
                            occurs.
        """

        params = {
            "state": json_pointer
        }

        try:
            response = self._rpc(method="get_state", rpc_timeout=5, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
            if response["result"] is None:
                return []
            else:
                return response["result"]
        except Exception as e:
            raise GED4KError(f"{str(e)}")

    def restart(self, exitcode: int = 117):
        """
        @brief Restart main application

        @param exitcode: The exit code for the main app (int).
        This code needs also to be set in the service file for restarting
        correctly.

        @return Reply message and exit code.

        @raises GED4KError: If a JSON-RPC error or an unexpected error
                            occurs.
        """

        params = {
            "code": exitcode
        }

        try:
            response = self._rpc(method="restart_main_app",
                                 rpc_timeout=5, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
            if response["result"] is None:
                return []
            else:
                return response["result"]
        except Exception as e:
            raise GED4KError(f"{str(e)}")

    def show_custom_testpicture(self, stream_idx, filepath):
        """
        @brief Show the given test picture on the screen
        @param stream_idx: Stream ID (int).
        @param filepath: Path to the desired file (str).

        @raises GED4KError: If a JSON-RPC error or an unexpected error
                            occurs.
        """

        format = os.path.splitext(filepath)[1][1:].lower()
        if format not in ("png", "dsc", "zip"):
            raise Exception(f"Unsupported picture format: {format}")
        content_type = None
        if format == "zip":
            content_type = os.path.splitext(filepath)[0][-3:]
            info = self.__file_upload(filepath, f"animation.{format}",
                                      progress=True)
        else:
            info = self.__file_upload(filepath, f"testpicture.{format}",
                                      progress=True)

        params = {
            "stream_idx": stream_idx,
            "format": format,
            "content_type": content_type,
            "path": info["path"]
        }

        try:
            response = self._rpc("show_custom_testpicture", 5.0, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
        except Exception as e:
            raise Exception(f"{str(e)}")

    def remove_custom_testpicture(self, stream_idx):
        """
        @brief Remove a custom test picture for the given stream
        @param stream_idx: Stream ID (int).

        @raises GED4KError: If a JSON-RPC error or an unexpected error
                            occurs.
        """

        params = {
            "stream_idx": stream_idx,
        }

        try:
            response = self._rpc("remove_custom_testpicture", 5.0, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
        except Exception as e:
            raise Exception(f"{str(e)}")

    def trigger_auto_alignment(self):
        """
        @brief  Force link autoalignment on the GED4K

        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs.
        """

        params = {
        }

        try:
            response = self._rpc("trigger_auto_alignment", 1.0, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
        except Exception as e:
            raise GED4KError(f"{str(e)}")

    def get_phy_params(self, display: Display):
        """
        @brief Get PHY params

        @param display: A Display instance

        @return: An array of variable length representing the
                 PHY parameters.

        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs
        """

        params = {
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
        }

        try:
            response = self._rpc(method="get_phy_params", **params, rpc_timeout=5)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
            if response["result"] is None:
                return []
            else:
                return response["result"]
        except Exception as e:
            raise GED4KError(f"getPhyParams: {str(e)}")

    def set_phy_params(self, display: Display, phy_params):
        """
        @brief Set PHY params

        @param display: A Display instance
        @param phy_params: An array of variable length representing the
                           new PHY parameters to set.

        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs
        """

        params = {
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
            "phyParams": phy_params
        }

        try:
            response = self._rpc(method="set_phy_params", **params, rpc_timeout=5)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
            if response["result"] is None:
                return []
            else:
                return response["result"]
        except Exception as e:
            raise GED4KError(f"setPhyParams: {str(e)}")

    def measure_eye_diagram(self, display: Display,
                            lane: int = 0,
                            mode: str = "low_res"):
        """
        @brief Start eye diagram measurement

        @pre register_callback_diag_job_finished must be called before,
             in order to register a callback retrieving the final result
        @post unregister_callback_diag_job_finished shall be called after
              the diagnostic job has finished

        @param display: A Display instance
        @param lane: APIX lane the measurement shall take place on
        @param mode: "high_res" or "low_res"
        """

        if mode != "low_res" and mode != "high_res":
            raise GED4KError(f"measure_eye_diagram: Invalid mode")

        params = {
            "job": "measure_eye_diagram",
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
            "lane": lane,
            "mode": mode
        }

        self.__start_diag_job(**params)

    def measure_rssi(self, display: Display, lane: int = 0):
        """
        @brief Start RSSI measurement on the GED4K

        @pre register_callback_diag_job_finished must be called before,
             in order to register a callback retrieving the final result
        @post unregister_callback_diag_job_finished shall be called after
              the diagnostic job has finished

        @param display: A Display instance
        @param lane: APIX lane the measurement shall take place on
        """

        params = {
            "job": "measure_rssi",
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
            "lane": lane,
        }

        self.__start_diag_job(**params)

    def measure_amplitude(self, display: Display, lane: int = 0):
        """
        @brief Start link amplitude measurement

        @pre register_callback_diag_job_finished must be called before,
             in order to register a callback retrieving the final result
        @post unregister_callback_diag_job_finished shall be called after
              the diagnostic job has finished

        @param display: A Display instance
        @param lane: APIX lane the measurement shall take place on
        """

        params = {
            "job": "measure_amplitude",
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
            "lane": lane,
        }

        self.__start_diag_job(**params)

    def measure_ber_downstream(self, display: Display,
                               lane: int = 0, time: int = 10):
        """
        @brief Start downstream bitrate error measurement

        @pre register_callback_diag_job_finished must be called before,
             in order to register a callback retrieving the final result
        @post unregister_callback_diag_job_finished shall be called after
              the diagnostic job has finished

        @param display: A Display instance
        @param lane: APIX lane the measurement shall take place on
        @param time: Measurement time (int)
        """

        params = {
            "job": "measure_ber_downstream",
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
            "lane": lane,
            "time": time
        }

        self.__start_diag_job(**params)

    def measure_ber_upstream(self, display: Display,
                             lane: int = 0, time: int = 10):
        """
        @brief Start upstream bit rate error measurement

        @pre register_callback_diag_job_finished must be called before,
             in order to register a callback retrieving the final result
        @post unregister_callback_diag_job_finished shall be called after
              the diagnostic job has finished

        @param display: A Display instance
        @param lane: APIX lane the measurement shall take place on
        @param time: Measurement time (int)
        """

        params = {
            "job": "measure_ber_upstream",
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
            "lane": lane,
            "time": time
        }

        self.__start_diag_job(**params)

    def run_test(self, display: Display, test_name: str, rpc_timeout: float = 80):
        """
        @brief Run protocol or link test

        @param display: A Display instance
        @param test_name: Name of test to run
        @param rpc_timeout: Timeout for RPC call in seconds

        @returns Test result (dictionary)
        @raises GED4KError: If a JSON-RPC error or an unexpected error occurs
        """

        params = {
            "display": self.__get_display_name(display.get_slot(),
                                               display.get_lane(),
                                               display.get_repeater()),
            "test": test_name,
        }

        try:
            response = self._rpc("run_test", rpc_timeout, **params)
            if "error" in response:
                raise Exception(f"{response['error']['message']}")
            if response["result"] is None:
                return {}
            else:
                return response["result"]
        except Exception as e:
            raise GED4KError(f"run_test: {str(e)}")

    def list_tests(self, display: Display):
        """
        @brief List all available protocol and link tests

        @param display: A Display instance

        @returns Test list (dictionary)
        @raises GED4KError: If a JSON-RPC error or unexpected error occurs
        """
        return self.run_test(display, "ls")

    class DiagWorker:
        def __init__(self, host, **params):
            self.params = params
            self.dut = self.params["display"]
            self.worker_finished_callback = None
            self.host = host

        def do_work(self):
            try:
                result = None
                self.__start_diagnostic_job(5.0)
                while True:
                    result = self.__get_diagnostics_job_state(5.0)
                    if 'result' in result.keys():
                        state = result["result"]["state"]
                        if state == "Ready":
                            break

                    time.sleep(1)

                if self.worker_finished_callback:
                    self.worker_finished_callback(result["result"])

            except Exception as e:
                result = {'DeviceUnderTest': self.params['display'],
                          'data': str(e),
                          'job': self.params['job'],
                          'state': 'Error'}
                self.worker_finished_callback(result)

        def __start_diagnostic_job(self, rpc_timeout: float = 10.0):
            result = self.host._rpc("run_diagnostics_job", rpc_timeout,
                                    **self.params)
            if 'result' in result.keys():
                return result['result']
            elif 'error' in result.keys():
                raise GED4KRpcError(result['error']['code'],
                                    result['error']['message'])
            else:
                raise Exception("Unknown Error")

        def __get_diagnostics_job_state(self, rpc_timeout: float = 10.0):
            params = {
                "display": self.dut
            }

            try:
                response = self.host._rpc("get_diagnostics_job_state",
                                          rpc_timeout, **params)
                if "error" in response:
                    raise Exception(f"{response['error']['message']}")
            except Exception as e:
                raise GED4KError(f"{str(e)}")

            return response

    class FlashingWorker:
        total_bytes = 0
        transferred_bytes = 0
        state = ""

        def __init__(self, host,
                     callback_progress,
                     callback_finished,
                     fw_btld, fw_swfl,
                     transfer_fw=True,
                     activate_fw=True,
                     slot=3,
                     lane=0,
                     repeater=0):

            self.flashing_rpc_revision = 1

            self.host = host
            if repeater is None:
                # Using glob pattern for selecting all displays on lane
                self.displays = f"{slot}:{lane}.*"
            else:
                # Using array for selecting single display
                self.displays = [f"{slot}:{lane}.{repeater}"]
            self.callback_progress = callback_progress
            self.callback_finished = callback_finished

            if not activate_fw:
                programming = "transfer_only"
            elif not transfer_fw:
                programming = "programming_only"
            elif repeater is not None:
                programming = "transfer_with_programming"
            else:
                # Daisy chain
                programming = "two_step_programming"

            # TODO
            self.params = {
                'displays': self.displays,
                'btld': fw_btld,
                'swfl': fw_swfl,
                'initial_reset': host.config['fw_flashing']['initial_reset'],
                'programming': programming,
                'flash_mode_confirm_timeout': host.config['fw_flashing']['flash_mode_confirm_timeout'],
                'chunk_transfer_timeout': host.config['fw_flashing']['chunk_transfer_timeout'],
                'memory_check_timeout': host.config['fw_flashing']['memory_check_timeout'],
                'fw_activation_timeout': host.config['fw_flashing']['fw_activation_timeout'],
                'commit_changes_timeout': host.config['fw_flashing']['commit_changes_timeout'],
                'shutdown_timeout': host.config['fw_flashing']['shutdown_timeout'],
                'timeout': host.config['fw_flashing']['timeout'],
            }

            self.set_flashing_test(**host.config['fw_flashing_test'])

        def run(self):
            info = ""

            try:
                # We need the destination path for the SW update RPC calls
                if self.params['btld']:
                    info = self.__upload_firmware_file(self.params['btld'])
                    self.params['btld'] = info['path']
                if self.params['swfl']:
                    info = self.__upload_firmware_file(self.params['swfl'])
                    self.params['swfl'] = info['path']

                # Set some non empty string to inform GED4k flashing which
                # use case to choose for programming-only mode.
                if self.params['btld'] == '':
                    self.params['btld'] = 'dummy'
                if self.params['swfl'] == '':
                    self.params['swfl'] = 'dummy'

                self.start_fw_flashing()

                while True:
                    p = self.get_fw_flashing_progress(self.host)
                    info = p['info'] if 'info' in p else ''
                    if self.flashing_rpc_revision == 0:
                        p['active'] = (p['phase'] not in ['FINISHED', 'FAILED', 'ABORTED'])

                    if p['active']:
                        self.transferred_bytes = int(p['transferred_bytes'])
                        self.total_bytes = int(p['total_bytes'])
                        self.callback_progress(p['phase'], info,
                                               self.transferred_bytes,
                                               self.total_bytes)
                    else:
                        self.state = p['phase']
                        if self.state == 'FINISHED':
                            self.transferred_bytes = self.total_bytes
                        break
                    time.sleep(0.1)

            except Exception as e:
                info = "Flash Update: " + str(e)
                print(info)
                self.state = 'FAILED'

            self.callback_finished(self.state, self.transferred_bytes, info)

        def set_flashing_test(self, **params):
            if type(self.displays) is list:
                for d in self.displays:
                    params['display'] = d
                    self.host._rpc("set_flashing_test", rpc_timeout=15.0, **params)
            else:
                params['displays'] = self.displays
                self.host._rpc("set_flashing_test", rpc_timeout=15.0, **params)

        def start_fw_flashing(self, rpc_timeout: float = 10.0):
            self.flashing_rpc_revision = 1
            result = self.host._rpc("flash_displays", rpc_timeout, **self.params)

            # When RPC fails with "Method not found" fallback to legacy RPC
            if 'error' in result.keys() and result['error']['code'] == -32601:
                self.flashing_rpc_revision = 0

                if isinstance(self.displays, str) or len(self.displays) > 1:
                    raise GED4KRpcError(result['error']['code'],
                                        "Flashing multiple displays is not supported by this GED4k SW version")

                if 'displays' in self.params:
                    del self.params['displays']
                self.params['display'] = self.displays[0]
                self.params['programming'] = self.params['programming'] != "transfer_only"
                result = self.host._rpc("flash_display", rpc_timeout, **self.params)

            if 'result' in result.keys():
                return result['result']
            elif 'error' in result.keys():
                raise GED4KRpcError(result['error']['code'],
                                    result['error']['message'])
            else:
                raise Exception("Unknown Error")

        def get_fw_flashing_progress(self, host, timeout: float = 15.0):
            params = {"displays": self.displays}

            if self.flashing_rpc_revision == 0:
                params = {"display": self.displays[0]}

            result = host._rpc("get_flashing_progress", timeout, **params)
            if "result" in result.keys():
                results = result["result"]

                if self.flashing_rpc_revision == 0:
                    return results

                if len(results) < 1:
                    raise Exception("Empty result")
                combined = {
                    "active": any(map(lambda r: r["active"], results.values())),
                    "transferred_bytes": sum(
                        map(lambda r: r["transferred_bytes"], results.values())
                    ),
                    "total_bytes": sum(
                        map(lambda r: r["total_bytes"], results.values())
                    ),
                }

                def combine(key: str, results):
                    first = next(iter(results.values()))
                    return (
                        first[key]
                        if all(
                            map(lambda r: r[key] == first[key], results.values())
                        )
                        else ", ".join(
                            [f"{dpy}: {res[key]}" for dpy, res in results.items()]
                        )
                    )

                for key in ["phase", "info"]:
                    combined[key] = combine(key, results)

                return combined
            elif "error" in result.keys():
                raise GED4KRpcError(result["error"]["code"],
                                    result["error"]["message"])
            else:
                raise Exception("Unknown Error")

        def __upload_firmware_file(self, filename):
            if not filename:
                raise Exception("GED4K FirmwareFlashing: No firmware file")

            url = "http://%s:%d/cgi-bin/fileupload.cgi" % (self.host.get_ip_addr(),
                                                           self.host.get_http_port())

            response = None
            proxies = {"http": None}
            local_hash = ""

            try:
                with open(filename, "rb") as f:
                    response = requests.post(url, files={'file': f},
                                             proxies=proxies)
                    f.seek(0)
                    data = f.read()
                    local_hash = hashlib.md5(data).hexdigest()
            except Exception as e:
                raise Exception("GED4K FirmwareFlashing: " + str(e))

            info = ""
            if response.status_code != 200:
                raise GED4KRpcError(str(response.status_code),
                                    str(response.content))
            else:
                info = json.loads(response.content)
                if info['md5sum'] != local_hash:
                    raise Exception("GED4K FirmwareFlashing: FW upload failed")

            return info

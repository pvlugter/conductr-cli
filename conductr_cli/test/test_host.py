from unittest import TestCase
from unittest.mock import patch, MagicMock, call
from conductr_cli import host
from conductr_cli.test.cli_test_case import strip_margin
import ipaddress
import socket


class TestResolveDefaultHost(TestCase):
    def test_resolve(self):
        resolve_default_ip_mock = MagicMock(return_value='resolve_result')
        with patch('conductr_cli.host.resolve_default_ip', resolve_default_ip_mock):
            result = host.resolve_default_host()
            self.assertEqual(result, 'resolve_result')

        resolve_default_ip_mock.assert_called_with()


class TestResolveDefaultIp(TestCase):
    def test_resolve_from_docker(self):
        is_listening_mock = MagicMock(return_value=False)
        vm_type_mock = MagicMock(return_value='vm_type')
        with patch('conductr_cli.host.is_listening', is_listening_mock), \
                patch('conductr_cli.docker.vm_type', vm_type_mock):
            result = host.resolve_default_ip()
            self.assertEqual(result, '127.0.0.1')

        is_listening_mock.assert_called_with(ipaddress.ip_address('192.168.10.1'), 9005)

    def test_resolve_from_addr_range(self):
        is_listening_mock = MagicMock(return_value=True)
        with patch('conductr_cli.host.is_listening', is_listening_mock):
            result = host.resolve_default_ip()
            self.assertEqual(result, '192.168.10.1')

        is_listening_mock.assert_called_with(ipaddress.ip_address('192.168.10.1'), 9005)


class TestResolveHostFromEnv(TestCase):
    def test_conductr_host_env_set(self):
        os_getenv_mock = MagicMock(return_value='conductr_host_env')
        with patch('os.getenv', os_getenv_mock):
            result = host.resolve_host_from_env()
            self.assertEqual(result, 'conductr_host_env')

        os_getenv_mock.assert_called_with('CONDUCTR_HOST', 'conductr_host_env')

    def test_conductr_ip_env_set(self):
        os_getenv_mock = MagicMock(side_effect=[None, 'conductr_ip_env'])
        with patch('os.getenv', os_getenv_mock):
            result = host.resolve_host_from_env()
            self.assertEqual(result, 'conductr_ip_env')

        os_getenv_mock.assert_has_calls([call('CONDUCTR_IP', None), call('CONDUCTR_HOST', None)])

    def test_no_env_set(self):
        os_getenv_mock = MagicMock(side_effect=[None, None])
        with patch('os.getenv', os_getenv_mock):
            result = host.resolve_host_from_env()
            self.assertEqual(result, None)

        os_getenv_mock.assert_has_calls([call('CONDUCTR_IP', None), call('CONDUCTR_HOST', None)])


class TestLoopbackDeviceName(TestCase):
    def test_linux(self):
        mock_system = MagicMock(return_value='Linux')
        with patch('platform.system', mock_system):
            self.assertEqual('lo', host.loopback_device_name())

    def test_macos(self):
        mock_system = MagicMock(return_value='Darwin')
        with patch('platform.system', mock_system):
            self.assertEqual('lo0', host.loopback_device_name())


class TestOsDetect(TestCase):
    def test_linux(self):
        mock_system = MagicMock(return_value='Linux')
        with patch('platform.system', mock_system):
            self.assertTrue(host.is_linux())
            self.assertFalse(host.is_macos())

    def test_macos(self):
        mock_system = MagicMock(return_value='Darwin')
        with patch('platform.system', mock_system):
            self.assertFalse(host.is_linux())
            self.assertTrue(host.is_macos())


class TestDisplayAddresses(TestCase):
    def test_output(self):
        addrs = [
            ipaddress.ip_address('192.168.1.1'),
            ipaddress.ip_address('192.168.1.2')
        ]
        self.assertEqual('192.168.1.1, 192.168.1.2', host.display_addrs(addrs))


class TestCanBind(TestCase):
    addr_ipv4 = ipaddress.ip_address('127.0.0.1')
    addr_ipv6 = ipaddress.ip_address('::1')
    port = 16371

    def test_success_ipv4(self):
        mock_socket = MagicMock()

        mock_bind = MagicMock()
        mock_socket.bind = mock_bind

        mock_close = MagicMock()
        mock_socket.close = mock_close

        mock_create_socket = MagicMock(return_value=mock_socket)

        with patch('socket.socket', mock_create_socket):
            self.assertTrue(host.can_bind(self.addr_ipv4, self.port))

        mock_create_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_bind.assert_called_once_with((self.addr_ipv4.exploded, self.port))
        mock_close.assert_called_once_with()

    def test_success_ipv6(self):
        mock_socket = MagicMock()

        mock_bind = MagicMock()
        mock_socket.bind = mock_bind

        mock_close = MagicMock()
        mock_socket.close = mock_close

        mock_create_socket = MagicMock(return_value=mock_socket)

        with patch('socket.socket', mock_create_socket):
            self.assertTrue(host.can_bind(self.addr_ipv6, self.port))

        mock_create_socket.assert_called_once_with(socket.AF_INET6, socket.SOCK_STREAM)
        mock_bind.assert_called_once_with((self.addr_ipv6.exploded, self.port))
        mock_close.assert_called_once_with()

    def test_failure(self):
        mock_socket = MagicMock()

        mock_bind = MagicMock(side_effect=OSError())
        mock_socket.bind = mock_bind

        mock_close = MagicMock()
        mock_socket.close = mock_close

        mock_create_socket = MagicMock(return_value=mock_socket)

        with patch('socket.socket', mock_create_socket):
            self.assertFalse(host.can_bind(self.addr_ipv6, self.port))

        mock_create_socket.assert_called_once_with(socket.AF_INET6, socket.SOCK_STREAM)
        mock_bind.assert_called_once_with((self.addr_ipv6.exploded, self.port))
        mock_close.assert_called_once_with()


class TestIsListening(TestCase):
    addr_ipv4 = ipaddress.ip_address('127.0.0.1')
    addr_ipv6 = ipaddress.ip_address('::1')
    port = 16371

    def test_listening_ipv4(self):
        mock_socket = MagicMock()

        mock_settimeout = MagicMock()
        mock_socket.settimeout = mock_settimeout

        mock_connect = MagicMock()
        mock_socket.connect = mock_connect

        mock_close = MagicMock()
        mock_socket.close = mock_close

        mock_create_socket = MagicMock(return_value=mock_socket)

        with patch('socket.socket', mock_create_socket):
            self.assertTrue(host.is_listening(self.addr_ipv4, self.port))

        mock_create_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_settimeout.assert_called_with(0.1)
        mock_connect.assert_called_once_with((self.addr_ipv4.exploded, self.port))
        mock_close.assert_called_once_with()

    def test_listening_ipv6(self):
        mock_socket = MagicMock()

        mock_settimeout = MagicMock()
        mock_socket.settimeout = mock_settimeout

        mock_connect = MagicMock()
        mock_socket.connect = mock_connect

        mock_close = MagicMock()
        mock_socket.close = mock_close

        mock_create_socket = MagicMock(return_value=mock_socket)

        with patch('socket.socket', mock_create_socket):
            self.assertTrue(host.is_listening(self.addr_ipv6, self.port))

        mock_create_socket.assert_called_once_with(socket.AF_INET6, socket.SOCK_STREAM)
        mock_settimeout.assert_called_with(0.1)
        mock_connect.assert_called_once_with((self.addr_ipv6.exploded, self.port))
        mock_close.assert_called_once_with()

    def test_not_listening(self):
        mock_socket = MagicMock()

        mock_settimeout = MagicMock()
        mock_socket.settimeout = mock_settimeout

        mock_connect = MagicMock(side_effect=OSError())
        mock_socket.connect = mock_connect

        mock_close = MagicMock()
        mock_socket.close = mock_close

        mock_create_socket = MagicMock(return_value=mock_socket)

        with patch('socket.socket', mock_create_socket):
            self.assertFalse(host.is_listening(self.addr_ipv4, self.port))

        mock_create_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_settimeout.assert_called_with(0.1)
        mock_connect.assert_called_once_with((self.addr_ipv4.exploded, self.port))
        mock_close.assert_called_once_with()


class TestAddrAliasSetupInstructions(TestCase):
    addr_range_ipv4 = ipaddress.ip_network('192.168.1.0/24')
    subnet_mask_ipv4 = addr_range_ipv4.netmask
    addrs_ipv4 = [
        ipaddress.ip_address('192.168.1.1'),
        ipaddress.ip_address('192.168.1.2')
    ]

    addr_range_ipv6 = ipaddress.ip_network('0:0:0:0:0:ffff:c0a8:101/128')
    subnet_mask_ipv6 = addr_range_ipv6.netmask
    addrs_ipv6 = [
        ipaddress.ip_address('0:0:0:0:0:ffff:c0a8:101'),
        ipaddress.ip_address('0:0:0:0:0:ffff:c0a8:102')
    ]

    loopback_device_name = 'ix0'

    def test_linux_ipv4(self):
        mock_loopback_device_name = MagicMock(return_value=self.loopback_device_name)
        mock_is_linux = MagicMock(return_value=True)
        mock_is_macos = MagicMock(return_value=False)

        with patch('conductr_cli.host.loopback_device_name', mock_loopback_device_name), \
                patch('conductr_cli.host.is_linux', mock_is_linux), \
                patch('conductr_cli.host.is_macos', mock_is_macos):
            result = host.addr_alias_setup_instructions(self.addrs_ipv4, self.subnet_mask_ipv4)

            expected_result = strip_margin("""|Whoops. Network address aliases are required so that the sandbox can operate as a cluster of machines.
                                              |
                                              |Please run the following and then try your command again:
                                              |
                                              |sudo ifconfig ix0:0 192.168.1.1 netmask 255.255.255.0 up
                                              |sudo ifconfig ix0:1 192.168.1.2 netmask 255.255.255.0 up
                                              |""")
            self.assertEqual(expected_result, result)

        mock_loopback_device_name.assert_called_once_with()
        mock_is_linux.assert_called_once_with()
        mock_is_macos.assert_not_called()

    def test_linux_ipv6(self):
        mock_loopback_device_name = MagicMock(return_value=self.loopback_device_name)
        mock_is_linux = MagicMock(return_value=True)
        mock_is_macos = MagicMock(return_value=False)

        with patch('conductr_cli.host.loopback_device_name', mock_loopback_device_name), \
                patch('conductr_cli.host.is_linux', mock_is_linux), \
                patch('conductr_cli.host.is_macos', mock_is_macos):
            result = host.addr_alias_setup_instructions(self.addrs_ipv6, self.subnet_mask_ipv6)

            expected_result = strip_margin("""|Whoops. Network address aliases are required so that the sandbox can operate as a cluster of machines.
                                              |
                                              |Please run the following and then try your command again:
                                              |
                                              |sudo ifconfig ix0:0 0000:0000:0000:0000:0000:ffff:c0a8:0101 netmask ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff up
                                              |sudo ifconfig ix0:1 0000:0000:0000:0000:0000:ffff:c0a8:0102 netmask ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff up
                                              |""")
            self.assertEqual(expected_result, result)

        mock_loopback_device_name.assert_called_once_with()
        mock_is_linux.assert_called_once_with()
        mock_is_macos.assert_not_called()

    def test_macos_ipv4(self):
        mock_loopback_device_name = MagicMock(return_value=self.loopback_device_name)
        mock_is_linux = MagicMock(return_value=False)
        mock_is_macos = MagicMock(return_value=True)

        with patch('conductr_cli.host.loopback_device_name', mock_loopback_device_name), \
                patch('conductr_cli.host.is_linux', mock_is_linux), \
                patch('conductr_cli.host.is_macos', mock_is_macos):
            result = host.addr_alias_setup_instructions(self.addrs_ipv4, self.subnet_mask_ipv4)

            expected_result = strip_margin("""|Whoops. Network address aliases are required so that the sandbox can operate as a cluster of machines.
                                              |
                                              |Please run the following and then try your command again:
                                              |
                                              |sudo ifconfig ix0 alias 192.168.1.1 255.255.255.0
                                              |sudo ifconfig ix0 alias 192.168.1.2 255.255.255.0
                                              |""")
            self.assertEqual(expected_result, result)

        mock_loopback_device_name.assert_called_once_with()
        mock_is_linux.assert_called_once_with()
        mock_is_macos.assert_called_once_with()

    def test_macos_ipv6(self):
        mock_loopback_device_name = MagicMock(return_value=self.loopback_device_name)
        mock_is_linux = MagicMock(return_value=False)
        mock_is_macos = MagicMock(return_value=True)

        with patch('conductr_cli.host.loopback_device_name', mock_loopback_device_name), \
                patch('conductr_cli.host.is_linux', mock_is_linux), \
                patch('conductr_cli.host.is_macos', mock_is_macos):
            result = host.addr_alias_setup_instructions(self.addrs_ipv6, self.subnet_mask_ipv6)

            expected_result = strip_margin("""|Whoops. Network address aliases are required so that the sandbox can operate as a cluster of machines.
                                              |
                                              |Please run the following and then try your command again:
                                              |
                                              |sudo ifconfig ix0 alias 0000:0000:0000:0000:0000:ffff:c0a8:0101 ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
                                              |sudo ifconfig ix0 alias 0000:0000:0000:0000:0000:ffff:c0a8:0102 ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
                                              |""")
            self.assertEqual(expected_result, result)

        mock_loopback_device_name.assert_called_once_with()
        mock_is_linux.assert_called_once_with()
        mock_is_macos.assert_called_once_with()

    def test_unknown_ipv4(self):
        mock_loopback_device_name = MagicMock(return_value=self.loopback_device_name)
        mock_is_linux = MagicMock(return_value=False)
        mock_is_macos = MagicMock(return_value=False)

        with patch('conductr_cli.host.loopback_device_name', mock_loopback_device_name), \
                patch('conductr_cli.host.is_linux', mock_is_linux), \
                patch('conductr_cli.host.is_macos', mock_is_macos):
            result = host.addr_alias_setup_instructions(self.addrs_ipv4, self.subnet_mask_ipv4)

            expected_result = 'Setup aliases for 192.168.1.1, 192.168.1.2 addresses with 255.255.255.0 subnet mask'
            self.assertEqual(expected_result, result)

        mock_loopback_device_name.assert_called_once_with()
        mock_is_linux.assert_called_once_with()
        mock_is_macos.assert_called_once_with()

    def test_unknown_ipv6(self):
        mock_loopback_device_name = MagicMock(return_value=self.loopback_device_name)
        mock_is_linux = MagicMock(return_value=False)
        mock_is_macos = MagicMock(return_value=False)

        with patch('conductr_cli.host.loopback_device_name', mock_loopback_device_name), \
                patch('conductr_cli.host.is_linux', mock_is_linux), \
                patch('conductr_cli.host.is_macos', mock_is_macos):
            result = host.addr_alias_setup_instructions(self.addrs_ipv6, self.subnet_mask_ipv6)

            expected_result = 'Setup aliases for ::ffff:c0a8:101, ::ffff:c0a8:102 addresses with ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff subnet mask'
            self.assertEqual(expected_result, result)

        mock_loopback_device_name.assert_called_once_with()
        mock_is_linux.assert_called_once_with()
        mock_is_macos.assert_called_once_with()

    def test_single_addr(self):
        mock_loopback_device_name = MagicMock(return_value=self.loopback_device_name)
        mock_is_linux = MagicMock(return_value=True)
        mock_is_macos = MagicMock(return_value=False)

        with patch('conductr_cli.host.loopback_device_name', mock_loopback_device_name), \
                patch('conductr_cli.host.is_linux', mock_is_linux), \
                patch('conductr_cli.host.is_macos', mock_is_macos):
            result = host.addr_alias_setup_instructions([self.addrs_ipv4[0]], self.subnet_mask_ipv4)

            expected_result = strip_margin("""|Whoops. Network address aliases are required so that the sandbox can operate as a cluster of machines.
                                              |
                                              |Please run the following and then try your command again:
                                              |
                                              |sudo ifconfig ix0:0 192.168.1.1 netmask 255.255.255.0 up
                                              |""")
            self.assertEqual(expected_result, result)

        mock_loopback_device_name.assert_called_once_with()
        mock_is_linux.assert_called_once_with()
        mock_is_macos.assert_not_called()

from cement.core import controller, foundation, backend
from cement.utils import test
from common.testutils import file_len, decallmethods
from droopescan import DroopeScan
from mock import patch, MagicMock
import responses

class BaseTest(test.CementTestCase):
    app_class = DroopeScan
    scanner = None

    base_url = "http://adhwuiaihduhaknbacnckajcwnncwkakncw.com/"

    param_base = ["--url", base_url, '-n', '10']
    param_plugins = param_base + ["-e", 'p']
    param_themes = param_base + ["-e", 't']
    param_version = param_base + ["-e", 'v']
    param_all = param_base + ["-e", 'a']

    def setUp(self):
        super(BaseTest, self).setUp()
        self.reset_backend()
        self.app = DroopeScan(argv=[],
            plugin_config_dir="./plugins.d",
            plugin_dir="./plugins")
        self.app.testing = True
        self.app.setup()

    def tearDown(self):
        self.app.close()

    def mock_controller(self, plugin_label, method, return_value = None, side_effect = None):
        """
            Mocks controller by label. Can only be used to test controllers
            that get instantiated automatically by cement.
            @param plugin_label e.g. 'drupal'
            @param method e.g. 'enumerate_plugins'
            @param return_value what to return. Default is None, unless the
                method starts with enumerate_*, in which case the result is a
                tuple as expected by BasePlugin.
            @param side_effect if set to an exception, it will raise an
                exception.
        """
        m = MagicMock()
        if return_value:
            m.return_value = return_value
        else:
            if method.startswith("enumerate_"):
                m.return_value = ({"a":[]}, True)

        if side_effect:
            m.side_effect = side_effect

        setattr(backend.__handlers__['controller'][plugin_label], method, m)
        return m

    def add_argv(self, argv):
        """
            Concatenates list with self.app.argv.
        """
        self.app._meta.argv += argv

    def assert_called_contains(self, mocked_method, kwarg_name, kwarg_value):
        args, kwargs = mocked_method.call_args
        assert kwargs[kwarg_name] == kwarg_value, "Parameter is not as expected."

    def respond_several(self, base_url, data_obj):
        for status_code in data_obj:
            for item in data_obj[status_code]:
                url = base_url % item
                responses.add(responses.HEAD, url,
                        body=str(status_code), status=status_code)

    def mock_all_enumerate(self, plugin_name, side_effect_on_one=False):
        all = []
        all.append(self.mock_controller("drupal", 'enumerate_plugins'))
        all.append(self.mock_controller("drupal", 'enumerate_themes'))
        if not side_effect_on_one:
            all.append(self.mock_controller("drupal", 'enumerate_users'))
        else :
            all.append(self.mock_controller("drupal", 'enumerate_users',
                side_effect=RuntimeError("derp!")))
        all.append(self.mock_controller("drupal", 'enumerate_version'))

        return all



#
# Copyright SAS Institute
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from __future__ import print_function
from IPython import display as dis
from IPython.core.display import HTML
from saspy.SASLogLexer import SASLogStyle, SASLogLexer
from pygments.formatters import HtmlFormatter
from pygments import highlight


class SASresults(object):
    """Return results from a SAS Model object"""

    def __init__(self, attrs, session, objname, nosub=False, log=''):

        if len(attrs) > 0:
           self._attrs = attrs
           if len(log)>0:
               self._attrs.append("LOG")
        else:
           self._attrs = ['ERROR_LOG']
        self._name = objname
        self.sas = session
        self.nosub = nosub
        self._log = log

    def __dir__(self) -> list:
        """Overload dir method to return the attributes"""
        return self._attrs

    def __getattr__(self, attr):
        if attr.startswith('_'):
            return getattr(self, attr)
        if attr.upper() == 'LOG' or attr.upper() == 'ERROR_LOG':
            if not self.sas.batch:
                return HTML(self._colorLog(self._log))
            else:
                return self._log
        if attr.upper() in self._attrs:
            data = self._go_run_code(attr)

        else:
            if self.nosub:
                print('This SAS Result object was created in teach_me_SAS mode, so it has no results')
                return
            else:
                print("Result named "+attr+" not found. Valid results are:"+str(self._attrs))
                return

        if not self.sas.batch:
           return HTML('<h1>' + attr + '</h1>' + data['LST'])
        else:
           return data

    def _colorLog(self,log:str)-> str:
        color_log = highlight(log, SASLogLexer(), HtmlFormatter(full=True, style=SASLogStyle, lineseparator="<br>"))
        return color_log

    def _go_run_code(self, attr) -> dict:
        code = '%%getdata(%s, %s);' % (self._name, attr)
        res = self.sas.submit(code)
        return res


    def sasdata(self, table) -> object:
        x = self.sas.sasdata(table, '_' + self._name)
        return x

    def ALL(self):
        """
        This method shows all the results attributes for a given object
        """
        if not self.sas.batch:
           for i in self._attrs:
               dis.display(self.__getattr__(i))
        else:
           ret = []
           for i in self._attrs:
               ret.append(self.__getattr__(i))
           return ret


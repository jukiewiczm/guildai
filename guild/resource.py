# Copyright 2017 TensorHub, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from guild import entry_point_util
from guild.model import ModelfileDistribution
from guild import namespace

_resources = entry_point_util.EntryPointResources("guild.resources", "resource")

class Resource(object):

    def __init__(self, ep):
        self.name = ep.name
        self.dist = ep.dist
        self.resdef = _resdef_for_dist(ep.name, ep.dist)
        self._fullname = None # lazy

    def __repr__(self):
        return "<guild.resource.Resource '%s'>" % self.name

    @property
    def fullname(self):
        if self._fullname is None:
            package_name = namespace.apply_namespace(self.dist.project_name)
            model_name = self.resdef.modeldef.name
            self._fullname = "%s/%s:%s" % (package_name, model_name, self.name)
        return self._fullname

def _resdef_for_dist(name, dist):
    if isinstance(dist, ModelfileDistribution):
        for model in dist.modelfile:
            for res in model.resources:
                if res.name == name:
                    return res
        raise ValueError(
            "cannot find resource '%s' in modefile %s"
            % (name, dist.modelfile.src))
    else:
        raise ValueError("unsupported resource distribution: %s" % dist)

def set_path(path):
    _resources.set_path(path)

def add_model_path(model_path):
    path = _resources.path()
    try:
        path.remove(model_path)
    except ValueError:
        pass
    path.insert(0, model_path)
    _resources.set_path(path)

def iter_resources():
    for _name, res in _resources:
        if not res.resdef.modeldef.private:
            yield res

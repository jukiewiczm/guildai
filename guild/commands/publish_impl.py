# Copyright 2017-2019 TensorHub, Inc.
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

from __future__ import absolute_import
from __future__ import division

import os

from guild import batch_util
from guild import cli
from guild import publish as publishlib
from guild import util

from . import runs_impl

def publish(args, ctx=None):
    if args.files and args.all_files:
        cli.error("--files and --all-files cannot both be used")
    if args.refresh_index:
        _refresh_publish_index(args)
    else:
        _publish(args, ctx)
    _report_dir_size(args)

def _publish(args, ctx):
    preview = (
        "You are about to publish the following run(s) to %s:"
        % (args.dest or publishlib.DEFAULT_DEST_HOME))
    confirm = "Continue?"
    no_runs = "No runs to publish."
    def publish_f(runs, formatted):
        _publish_runs(runs, formatted, args)
        _refresh_publish_index(args, no_dest=True)
    def select_runs_f(args, ctx, default_runs_arg, force_deleted):
        runs = runs_impl.runs_op_selected(args, ctx, default_runs_arg, force_deleted)
        return [
            run for run in runs
            if args.include_batch or not batch_util.is_batch(run)
        ]
    runs_impl.runs_op(
        args, ctx, False, preview, confirm, no_runs,
        publish_f, runs_impl.ALL_RUNS_ARG, True, select_runs_f)

def _publish_runs(runs, formatted, args):
    if args.all_files:
        copy_files = publishlib.COPY_ALL_FILES
    elif args.files or args.include_links:
        copy_files = publishlib.COPY_DEFAULT_FILES
    else:
        copy_files = None
    for run, frun in zip(runs, formatted):
        cli.out("Publishing [%s] %s... " % (
            frun["short_id"],
            frun["operation"]), nl=False)
        frun["_run"] = run
        try:
            publishlib.publish_run(
                run,
                dest=args.dest,
                template=args.template,
                copy_files=copy_files,
                include_links=args.include_links,
                md5s=not args.no_md5,
                formatted_run=frun)
        except publishlib.PublishError as e:
            cli.error(
                "error publishing run %s:\n%s"
                % (run.id, e))
        else:
            dest = args.dest or publishlib.DEFAULT_DEST_HOME
            size = util.dir_size(os.path.join(dest, run.id))
            cli.out("using %s" % util.format_bytes(size))

def _refresh_publish_index(args, no_dest=False):
    if no_dest:
        dest_suffix = ""
    else:
        dest_suffix = " in %s" % (args.dest or publishlib.DEFAULT_DEST_HOME)
    print("Refreshing runs index%s" % dest_suffix)
    publishlib.refresh_index(args.dest)

def _report_dir_size(args):
    dest = args.dest or publishlib.DEFAULT_DEST_HOME
    size = util.dir_size(dest)
    cli.out("Published runs using %s" % util.format_bytes(size))

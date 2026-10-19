---
title: From Pilot Shell 11
description: Use QualityLayer alongside Pilot Shell 11 and move at your own pace.
---

QualityLayer is a separate product. Version 11 is the last version called Pilot Shell, and you can keep using it for as long as you want. You can also use both products in parallel. Installing QualityLayer leaves Pilot Shell, its configuration and its tools in place.

## Start using QualityLayer

[Install QualityLayer](install.md), then ask your agent to plan or implement using QualityLayer or QL. Your existing paid Pilot Shell licence carries over at its existing price. Without an active licence, you can start a fresh seven-day QualityLayer trial, even if you already used a Pilot Shell trial.

Your repositories, code and Pilot plans stay where they are. QualityLayer starts its own tasks; it does not convert in-progress Pilot plans.

## Import memories per project

In QualityLayer, open **Settings → Memory → Import from Pilot Shell**, select the matching project, then choose its Pilot memory files from `.pilot/memories/` in that repository. The importer accepts JSONL and Markdown files. The project name on a memory must match the selected project.

The import copies lessons into QualityLayer's private project memory. It leaves the source files in place and skips unchanged lessons when you import them again. This is the only data you need to import. See [Pilot memory import](memory.md#import-pilot-lessons) for file formats and the CLI command.

## Remove Pilot Shell when you are ready

Once your workflows work in QualityLayer, use [Pilot Shell's own uninstaller](https://github.com/maxritter/pilot-shell/blob/v11.0.5/uninstall.sh) if you want to remove it. That uninstaller lets you decide which tools to keep. QualityLayer does not run it or remove Pilot Shell's tools for you.

Next: [your first QualityLayer task](first-task.md).

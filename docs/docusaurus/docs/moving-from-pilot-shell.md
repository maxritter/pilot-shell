---
title: From Pilot Shell 11
description: Use QualityLayer alongside Pilot Shell 11 and move at your own pace.
---

QualityLayer is a separate product. Version 11 is the last version called Pilot Shell, and you can keep using it for as long as you want. You can also use both products in parallel. Installing QualityLayer leaves Pilot Shell, its configuration and its tools in place.

## Update from Pilot Shell

Run `pilot update` in a terminal. Pilot Shell shows the update from v11 to v12 with its release notes and asks **Update now?**. When you confirm:

1. QualityLayer's installer starts and says that Pilot Shell is now QualityLayer and keeps working.
2. On a Mac, or Linux with a screen, it installs the QualityLayer App and its command line. Over SSH, in WSL or in a container, it installs the command line alone.
3. It adds the QualityLayer skills to each agent it finds, such as Claude Code and Codex. Every download is checked against the signed release before anything is written.
4. The App opens to finish setting up. If it cannot open a window, the installer says where the App is.

You can also [install QualityLayer](install.md) directly; the result is the same.

## Start using QualityLayer

Ask your agent to plan or implement using QualityLayer or QL. Your existing paid Pilot Shell licence carries over at its existing price. Without an active licence, you can start a fresh seven-day QualityLayer trial, even if you already used a Pilot Shell trial.

Your repositories, code and Pilot plans stay where they are. QualityLayer starts its own tasks; it does not convert in-progress Pilot plans.

## Import memories per project

In QualityLayer, open **Settings → Memory → Import from Pilot Shell**, select the matching project, then choose its Pilot memory files from `.pilot/memories/` in that repository. The importer accepts JSONL and Markdown files. The project name on a memory must match the selected project.

The import copies lessons into QualityLayer's private project memory. It leaves the source files in place and skips unchanged lessons when you import them again. This is the only data you need to import. See [Pilot memory import](memory.md#import-pilot-lessons) for file formats and the CLI command.

## Remove Pilot Shell when you are ready

Once your workflows work in QualityLayer, you can remove Pilot Shell with its own uninstaller:

```bash
curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/uninstall.sh | bash
```

It asks before removing anything and keeps the tools Pilot Shell installed; add `--remove-tools` to remove those too. QualityLayer does not run it or remove Pilot Shell's tools for you.

Next: [your first QualityLayer task](first-task.md).

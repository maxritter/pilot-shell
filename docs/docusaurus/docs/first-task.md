---
title: Your first task
description: One change, from your request to your approval, in seven steps.
---

![Your first task in seven steps: describe the change, answer its questions, approve the Plan, start Implement, agents build and check, settle what is left, approve the change](pathname:///img/diagrams/firsttask-light.svg)
![Your first task in seven steps: describe the change, answer its questions, approve the Plan, start Implement, agents build and check, settle what is left, approve the change](pathname:///img/diagrams/firsttask-dark.svg)

Pick a medium-sized feature in a repository you know. Opus 5.5 is recommended for this session. On a new computer, Home shows "Start your first task" with the command ready to copy.

Your agent asks each decision in the terminal, and the App beside it shows only what the current question is about. Put the App on the left and the terminal on the right. The App folds everything else and records each answer as "answered in the chat".

1. **Describe it.** `/ql add a CSV export to the reports page` (`$ql` in Codex). The task appears in the App as soon as your agent starts it.
2. **Answer its questions.** Your agent reads the code, then asks one question at a time in its picker, each with its recommendation. Then it asks whether **Done means** is what you asked for.
3. **Approve the Plan.** Your agent asks each engineering decision of the Plan, Agree or Change. The App shows the diagram or mockup the question is about; comment there on anything you are not asked. The last question is "Approve the Plan?", with Approve, Request changes or Review in the App first. Answer it in the terminal, or with the App's Approve button.
4. **Start Implement.** The App opens Implement by itself, with the setup it recommends for the build and one command to copy. Adjust the model or effort if you like, and paste the command into a terminal.
5. **Agents build and check.** Each task starts with a failing test. Nothing waits for you. When something does not go as planned, your agent takes the recommended way and lists it under **Changed while building**. You see the slices fill in, and later one checklist of everything that was checked.
6. **Settle what is left.** Whatever stays open reaches the final review. Your agent asks it in the terminal: confirm what only you can, look at the result, and accept or fix what the checks found.
7. **Approve the change.** Answer the last question in the terminal, or choose **Approve and open a pull request** in the App's Approve menu, or **Approve only**.

Next: [The App](app.md) shows how every step is laid out. Then [Discuss](steps/discuss.md), the first of the five steps.

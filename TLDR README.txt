Keep ONE copy of "Claude-vlpWorkflow" next to your projects. Do NOT copy it
inside a project, and do NOT copy its commands anywhere: the kit is a Claude
Code PLUGIN, it is loaded where it sits. There were six copies once, 500 lines
apart from each other, and nothing warned about it. Now there are none.

  ProgPerso/
    Claude-vlpWorkflow/   <- the kit, once
    MyProject/            <- your projects, next to it
    AnotherProject/

Get it once:

    git clone https://github.com/SebastienGrana/Claude-vlpWorkFlow.git

Install it once per machine, by LINKING it into ~/.claude/skills/ (a folder
there with a .claude-plugin/plugin.json loads by itself, in every project, no
marketplace needed -- and the folder may be a link, so nothing is copied).

Windows (PowerShell, no admin rights needed):

    New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\vlp" -Target "<path>\Claude-vlpWorkflow"

macOS / Linux:

    ln -s "<path>/Claude-vlpWorkflow" ~/.claude/skills/vlp

Then, in Claude-Code, move into the project folder (with the cd command in
claude's terminal) and type  /vlp:init  in the chat, and follow the
instructions.


Do not commit this folder INTO one of your projects' repositories. The kit
has its own repository -- https://github.com/SebastienGrana/Claude-vlpWorkFlow
-- and lives beside your projects, never inside one.




vlpWorkflow has 4 commands. They are all prefixed with the plugin name:

/vlp:init        ->   activate a new project

/vlp:chantier    ->   start a new work (a work = list of tasks)

/vlp:tache       ->   start the next task in the list

/vlp:check       ->   check a project: files, ticked boxes, published page,
                      costs. It only measures and reports, it never writes.


There used to be a fifth one, /vlp-sync, which pushed the kit's commands to
~/.claude/commands. It is gone, kept in archive/ for reference: there is no
copy to push any more. You edit the kit, and the next session reads what you
just wrote. Use /reload-plugins to see it in the current session.


The kit holds the ENGINE: the commands, the method, the templates. A project
holds only its DATA: CHANTIER.md, its state, its task files, its pages. This
is why the method file is not copied into projects any more -- one fix in the
kit now reaches every project at once.

Projects equipped before that rule keep their own copy; nothing is taken away
from them.


Each project also gets two published pages (Artifacts), kept up to date by the
commands: one road map for the project, one page per work with its task list.
Their links are stored in CHANTIER.md. See ARTEFACTS.md.

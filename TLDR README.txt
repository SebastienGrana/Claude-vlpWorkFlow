Keep ONE copy of "Claude-vlpWorkflow" next to your projects. Do NOT copy it
inside a project: a copy put there never gets updated. There were six copies
once, 500 lines apart from each other, and nothing warned about it.

  ProgPerso/
    Claude-vlpWorkflow/   <- the kit, once
    MyProject/            <- your projects, next to it
    AnotherProject/

Install the commands once per machine:

    cp Claude-vlpWorkflow/commands/*.md ~/.claude/commands/

Then, in Claude-Code, move into the project folder (with the cd command in
claude's terminal) and type  /vlp-init  in the chat, and follow the
instructions.


This folder should not be pushed on Git.




vlpWorkflow have 5 commands:

/vlp-init    ->   activate a new project

/chantier    ->   start a new work (a work = list of tasks)

/tache       ->   start the next task in the list

/vlp-sync    ->   push the kit's commands to ~/.claude/commands (after you
                  changed the kit -- always edit the kit, never the copy)

/vlp-check   ->   check a project: files, ticked boxes, published page, costs.
                  It only measures and reports, it never writes.


The kit holds the ENGINE: the commands, the method, the templates. A project
holds only its DATA: CHANTIER.md, its state, its task files, its pages. This
is why the method file is not copied into projects any more -- one fix in the
kit now reaches every project at once.

Projects equipped before that rule keep their own copy; nothing is taken away
from them.


Each project also gets two published pages (Artifacts), kept up to date by the
commands: one road map for the project, one page per work with its task list.
Their links are stored in CHANTIER.md. See ARTEFACTS.md.

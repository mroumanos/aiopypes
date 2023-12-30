from .task import Task


class Graph:

    """
    [0] every_second (n=1)
     |
     *--> [0] route_a (n=1)
     |     |
     |     *--> [0] task1 (n=50) --*
     |     *--> [0] task2 (n=50) --*
     |                             |
     *--> [0] route_b (n=1)        |
           |                       |
           *--> [0] task1 (n=50) --*
           *--> [0] task2 (n=50) --*
                                   |
                                   *--> [10] task4 (n=1)
    """

    def __init__(self, root: Task):
        self.root = root
    
    def print(self):
        g = ""
        pointer = set()
        pointer.add(self.root)
        v_offset = 0
        h_offset = 0
        while pointer:
            new_pointer = set()
            if v_offset > 0:
                g += "\n" * v_offset + " " * h_offset-6 + "|"
                v_offset += 1
            for task in list(pointer):
                if h_offset > 0:
                    stdscr.addstr(v_offset, h_offset-6, "*-->")
                g += self.node(task)
                for o in task.output:
                    new_pointer.add(o)
                v_offset += 1
            h_offset += 7
            pointer = new_pointer

    def node(self, task: Task):
        return f"[{task.input.queue.qsize()}] {task.name} (n={len(task.runners)})"
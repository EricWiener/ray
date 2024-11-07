import abc
from typing import Iterator, List, Callable


class Operator:
    """Abstract class for operators.

    Operators live on the driver side of the Dataset only.
    """

    def __init__(
        self,
        name: str,
        input_dependencies: List["Operator"],
    ):
        self._name = name
        self._input_dependencies = input_dependencies
        self._output_dependencies = []
        for x in input_dependencies:
            assert isinstance(x, Operator), x
            x._output_dependencies.append(self)

    @property
    def name(self) -> str:
        return self._name

    @property
    def input_dependencies(self) -> List["Operator"]:
        """List of operators that provide inputs for this operator."""
        assert hasattr(
            self, "_input_dependencies"
        ), "Operator.__init__() was not called."
        return self._input_dependencies

    @property
    def output_dependencies(self) -> List["Operator"]:
        """List of operators that consume outputs from this operator."""
        assert hasattr(
            self, "_output_dependencies"
        ), "Operator.__init__() was not called."
        return self._output_dependencies

    def post_order_iter(self) -> Iterator["Operator"]:
        """Depth-first traversal of this operator and its input dependencies."""
        for op in self.input_dependencies:
            yield from op.post_order_iter()
        yield self

    def transform(self, fn: Callable[["Operator"], "Operator"]) -> "Operator":
        # TODO add py-doc

        changed = False
        new_input_ops = []

        for op in self._input_dependencies:
            new_op = fn(op)
            new_input_ops.append(new_op)

            changed |= new_op != op

        # Make a copy if changed
        if changed:
            return self._copy(input_ops=new_input_ops)

        # Otherwise (no changes), return
        return self

    @abc.abstractmethod
    def _copy(self, input_ops: List["Operator"]):
        pass

    def __repr__(self) -> str:
        if self.input_dependencies:
            out_str = ", ".join([str(x) for x in self.input_dependencies])
            out_str += " -> "
        else:
            out_str = ""
        out_str += f"{self.__class__.__name__}[{self._name}]"
        return out_str

    def __str__(self) -> str:
        return repr(self)

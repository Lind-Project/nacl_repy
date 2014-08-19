import safe
import nanny
import emulmisc
import namespace
import repyportability
import virtual_namespace




def _do_nothing(*args):
  pass


def _initialize_safe_module():
    """
    A helper private function that helps initialize
    the safe module.
    """

    

    # Allow the user to do try, except, finally, etc.
    safe._NODE_CLASS_OK.append("TryExcept")
    safe._NODE_CLASS_OK.append("TryFinally")
    safe._NODE_CLASS_OK.append("Raise")
    safe._NODE_CLASS_OK.append("ExcepthandlerType")
    safe._NODE_CLASS_OK.append("Invert")
    safe._NODE_CLASS_OK.append("Import")
    
    # needed for traceback
    # NOTE: still needed for tracebackrepy
    safe._BUILTIN_OK.append("isinstance")
    safe._BUILTIN_OK.append("BaseException")
    safe._BUILTIN_OK.append("WindowsError")
    safe._BUILTIN_OK.append("type")
    safe._BUILTIN_OK.append("issubclass")
    # needed to allow primitive marshalling to be built
    safe._BUILTIN_OK.append("ord")
    safe._BUILTIN_OK.append("chr")
    safe._BUILTIN_OK.append("__import__")

    safe._STR_OK.append("__repr__")
    safe._STR_OK.append("__str__")
    # allow __ in strings.   I'm 99% sure this is okay (do I want to risk it?)
    safe._NODE_ATTR_OK.append('value')

    safe.serial_safe_check = _do_nothing
    safe._check_node = _do_nothing





def run_unrestricted_repy_code(filename, args_list=[]):
    """
    <Purpose>
        This function allows an user to run a repy file without
        using any restrictions like a normal repy program.

    <Arguments>
        filename - The filename of the repy file you want to run.

        args_list - a list of arguments that need to be passed in
            to the repy file.

    <Exceptions>
        Exception raised if args_list provided is not in the list form.

        Any exception raised by the repy file will be raised.

        Error may be raised if the code in the repy file is not safe.

    <Return>
        None
    """

    if not isinstance(args_list, list):
        raise Exception("args_list must be of list type!")

    # Initialize the safe module before building the context.
    _initialize_safe_module()

    # Prepare the callargs list
    callargs_list = [filename]
    callargs_list.extend(args_list)

    # Prepare the context.
    context = {}
    namespace.wrap_and_insert_api_functions(context)
    context = safe.SafeDict(context)
    context["_context"] = context
    context["createvirtualnamespace"] = virtual_namespace.createvirtualnamespace
    context["getlasterror"] = emulmisc.getlasterror
    context['callfunc'] = 'initialize'
    context['callargs'] = callargs_list


    code = open("dylink.repy").read()

    virt = virtual_namespace.VirtualNamespace(code, name="dylink_code")
    result = virt.evaluate(context) 

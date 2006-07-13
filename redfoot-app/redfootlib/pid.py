import sys, os, errno, logging

_logger = logging.getLogger("redfoot")

def check_file(pid_file):
    if os.path.exists(pid_file):
        try:
            pid = int(open(pid_file).read())
        except ValueError:
            sys.exit('PID file %s contains non-numeric value' % pid_file)
        try:
            os.kill(pid, 0)
        except OSError, why:
            if why[0] == errno.ESRCH:
                # The pid doesnt exists.
                _logger.info('Removing stale PID file %s' % pid_file)
                os.remove(pid_file)
            else:
                sys.exit("Can't check status of PID %s from file %s: %s" %
                         (pid, pid_file, why[1]))
        else:
            sys.exit("""\
Another redfoot daemon is running, PID %s\n
To run more than one daemon in the same directory use the --name parameter to give them distinct names.
""" %  pid)

def add_file(pid_file):
    file(pid_file, 'wb').write(str(os.getpid()))
        
def remove_file(pid_file):
    try:
        os.unlink(pid_file)
    except OSError, e:
        if e.errno == errno.EACCES or e.errno == errno.EPERM:
            _logger.warn("Warning: No permission to delete pid file")
        else:
            _logger.warn("Failed to unlink PID file:")
    except:
        _logger.warn("Failed to unlink PID file:")


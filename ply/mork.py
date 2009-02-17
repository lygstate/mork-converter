import sys
import getopt

import output

def usage(msg=None):
    if msg:
        print >> sys.stderr, msg
    print >> sys.stderr, ('usage: %s [--tokens|--syntax|--format=<outformat>]'
        ' [--help] [file ...]' % sys.argv[0])
    print >> sys.stderr, ('  <outformat> has the form'
        ' <filtername>[:arg1[=val1]...[:argN[=valN]]]')
    print >> sys.stderr, '  Available filters and options:'

    for filtName, filtModule in output.iterFilters():
        print >> sys.stderr, '    %s' % filtName
        for (argName, argDescription) in filtModule.usage:
            print >> sys.stderr, '      %s: %s' % (argName, argDescription)

def splitFilterArgs(nameAndArgs):
    pieces = nameAndArgs.split(':')
    filterName = pieces[0]
    args = pieces[1:]

    argDict = {}
    for arg in args:
        pieces = arg.split('=', 1)
        argName = pieces[0]
        if len(pieces) == 1:
            argVal = ''
        else:
            argVal = pieces[1]

        argDict[argName] = argVal

    return (filterName, argDict)

def printTokens(f):
    import morklex
    morklex.printTokens(f)

def printSyntaxTree(f):
    import morkyacc
    tree = morkyacc.parseFile(f)
    print tree

def filterFile(f, module, moduleArgs):
    import morkdb
    import morkyacc

    tree = morkyacc.parseFile(f)
    db = morkdb.MorkDatabase.fromAst(tree)
    module.output(db, moduleArgs)

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    try:
        (options, arguments) = getopt.getopt(args, 'h',
            ['tokens', 'syntax', 'help', 'format='])
    except getopt.GetoptError, e:
        usage(str(e))
        return 2

    tokens = False
    syntax = False
    formatGiven = False
    format = 'csv:singlefile'

    for (opt, val) in options:
        if opt in ('-h', '--help'):
            usage()
            return 0
        elif opt == '--tokens':
            tokens = True
        elif opt == '--syntax':
            syntax = True
        elif opt == '--format':
            formatGiven = True
            format = val

    mutualyExclusive = [opt for opt in (tokens, syntax, formatGiven) if opt]
    if len(mutualyExclusive) > 1:
        usage('choose one (or zero) of --tokens, --syntax, or --format')
        return 2

    if len(arguments) == 0:
        arguments = ['-']

    if not tokens and not syntax:
        (filterName, filterArgs) = splitFilterArgs(format)
        filterModule = output.getFilter(filterName)

    for arg in arguments:
        if arg == '-':
            f = sys.stdin
        else:
            f = open(arg)

        if tokens:
            printTokens(f)
        elif syntax:
            printSyntaxTree(f)
        else:
            filterFile(f, filterModule, filterArgs)


if __name__ == '__main__':
    sys.exit(main())

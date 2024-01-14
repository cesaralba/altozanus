from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, BooleanOptionalAction
from collections import Counter
from itertools import product
from random import choice
from time import clock_gettime_ns, sleep

from voicebox import SimpleVoicebox
from voicebox.tts import ESpeakConfig, ESpeakNG

CLOCK = 0
CANTNATURALES = 3
DEFFREC = 20
nSinSecs = 1.0 / 1000000000

numNotas = 100


def mensaje(txt, quiet, speaker):
    if quiet:
        print(txt)
    else:
        speaker.say(txt + " ")


def main(args):
    voicebox = None if args.quiet else SimpleVoicebox(tts=ESpeakNG(config=ESpeakConfig(voice="es-es")), effects=[], )

    strAcorde = ""
    pideAcordes: bool = args.acordes
    pideSemitonos: bool = (not pideAcordes) and args.semitonos

    manosTxt = "izquierda derecha"
    notasTxt = "Do Re Mi Fa Sol La Si"
    notasSost = "Do Re Fa Sol La"
    notasBemol = "Re Mi Sol La Si"

    manos = [args.mano]
    if args.mano == 'ambas':
        manos = manosTxt.split(" ")

    if pideAcordes:
        strAcorde = "acorde con "
    frec = args.frecuencia
    periodo = 60.0 / frec

    naturales = list(product(notasTxt.split(" "), " "))
    multNaturales = args.natural
    if pideSemitonos:
        semitonos = list(product(notasBemol.split(" "), ["bemol"])) + list(product(notasSost.split(" "), ["sostenido"]))
    else:
        semitonos = []
        multNaturales = 1

    notasCand = naturales * multNaturales + semitonos
    candidatos = list(product(manos, notasCand))

    resultados = []

    msgStart = "Comenzamos "
    mensaje(msgStart, args.quiet, voicebox)
    sleep(args.pausaInicial)

    msgStart = "Vamos a ello "
    mensaje(msgStart, args.quiet, voicebox)

    if not args.quiet:
        sleep(2)

    for _ in range(args.numNotas):
        mano, (nota, tono) = choice(candidatos)
        resultados.append((mano, (nota, tono)))
        ahora = clock_gettime_ns(CLOCK)
        mandato = f"{strAcorde} Mano {mano} {nota} {tono} "
        mensaje(mandato, args.quiet, voicebox)

        after = clock_gettime_ns(CLOCK)
        durac = (after - ahora) * nSinSecs

        espera = max([0.0, (periodo - durac)])
        print(f"{mandato} -> {ahora} f:{frec} T:{periodo} {after} Durac = {durac} Espera {espera}")
        sleep(espera)

    mensaje("Gracias", args.quiet, voicebox)

    print(Counter(resultados))


def ProcesaArgumentos():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', dest='verbose', action="count", required=False, help='', default=0)
    parser.add_argument('-d', dest='debug', action="store_true", required=False, help='', default=False)

    parser.add_argument('-n', '--numnotas', dest='numNotas', action="store", required=False,
                        help='Numero de notas a poner', default=100, type=int)
    parser.add_argument('-f', '--freq', dest='frecuencia', action="store", required=False,
                        help='Numero de notas por minuto', default=DEFFREC, type=float)
    parser.add_argument('-x', '--natural', dest='natural', action="store", required=False,
                        help="Numero de escalas 'naturales' a usar", default=CANTNATURALES)

    parser.add_argument('-m', '--mano', dest='mano', action="store", required=False,
                        choices=['izquierda', 'derecha', 'ambas'], help='Mano a usar', default="ambas")
    parser.add_argument('-p', '--pausa', dest='pausaInicial', action="store", help='Pausa antes de empezar',
                        required=False, default=30, type=float)

    parser.add_argument('-s', '--semitonos', dest='semitonos', action=BooleanOptionalAction,
                        help='Pide semitonos (sostenido o bemol)', required=False, default=True)

    parser.add_argument('-a', '--acordes', dest='acordes', action=BooleanOptionalAction, help='Pide acordes',
                        required=False, default=False)

    parser.add_argument('-q', '--quiet', dest='quiet', action="store_true", help='Sin sonido', required=False,
                        default=False)

    args = parser.parse_args()

    return args


##########################


if __name__ == '__main__':
    args = ProcesaArgumentos()
    print(args)
    main(args)

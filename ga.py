#===============================================================#
# ga.py                                                         #
# Implementation of a genetic algorithm demonstration as found  #
# at www.ai-junkie.com.                                         #
# Original problem and C++ code by Mat Buckland aka fup.        #
# Author: Yati Sagade (yati [dot] sagade [at] gmail [dot] com)  #
#===============================================================#
from random import random
import math
import expr
from copy import copy

CROSSOVER_RATE              = 0.7
MUTATION_RATE               = 0.001
POP_SIZE                    = 100

# Not used at all here, but was there in Fup's C++ code.
CHROMO_LENGTH               = 300

# Length of each gene - For our purpose, 4 bits are enough.
GENE_LENGTH                 = 4

# Number of times to try before we give up :P
MAX_ALLOWABLE_GENERATIONS   = 400

OPERATORS = ['+', '-', '*', '/']
                
# ==============================================================#
# Chromosome                                                    #
# - The class that represents a chromosome                      #
# Corresponds to chromo_type in the C++ code.                   #
# ==============================================================#
class Chromosome:
    def __init__(self, bits="", fitness=0.0):
        self.bits = bits
        self.fitness = fitness

    def length(self):
        return len(self.bits)
#----------------------------------------------------------------
def crossover(offspring1, offspring2):
    '''Takes two Chromosome objects, and crosses over their parts 
    as determined by the crossover rate.

    *Note: I've used the greater of the lengths of the two
    chromosomes to determine the crossover position. Fup's code 
    uses CHROMO_LENGTH to do the same.
    '''
    if random() < CROSSOVER_RATE:
        cpos = int(random() * max(offspring1.length(), offspring2.length()))
        offspring1.bits, offspring2.bits = (
                                  offspring1.bits[:cpos] + offspring2.bits[cpos:], 
                                  offspring2.bits[:cpos] + offspring1.bits[cpos:]
                                 )
        return True

    return False
#----------------------------------------------------------------
def mutate(chromosome):
    '''Steps through each "bit" in the chromosome, and as determined
    by the mutation rate, flips the bit. 
    '''
    result = []
    ret = False
    for bit in chromosome.bits:
        prob = random()
        if prob < MUTATION_RATE:
            result.append(int(not int(bit)))
            ret = True
        else:
            result.append(int(bit))

    chromosome.bits = ''.join(map(str, result))
    return ret
#----------------------------------------------------------------
def decode(chromosome, symbolize_ops=False):
    '''Takes a chromosome, and decodes it.
    The result is returned as a list of tokens.

    If symbolize_ops is true, operator symbols are used in the result
    instead of operator values.

    e.g., if the bit pattern is '100110101000', the result when
    symbolize_ops is True is:
        [9, '+', 8]
    else, it is 
        [9, 10, 8]
    '''
    op = False
    mapping = {10: '+', 11: '-', 12: '*', 13: '/'}
    result = []
    for i in xrange(0, chromosome.length(), GENE_LENGTH):
        val = int(chromosome.bits[i: (i + GENE_LENGTH)], 2)
        if op:
            if val < 10 or val > 13:
                continue
            if symbolize_ops:
                result.append(mapping[val])
            else:
                result.append(val)
            op = False
        else:
            if val > 9:
                continue
            result.append(val)
            op = True

    return result
#----------------------------------------------------------------
def decode_as_str(chromosome):
    '''return the decoded chromosome as an str'''
    decoded = decode(chromosome, symbolize_ops=True)
    return ' '.join(map(str, decoded))
#----------------------------------------------------------------
def encode(e):
    '''takes an expression array and returns a bitstring.
    See decode() on how the expression string should look like.
    '''
    encoded = ''
    for token in e:
        if expr.is_numeral(token):
            val = bin(token)[2:]    # bin returns the binary rep of a number prefixed with a '0b' - the [2:] takes...
            val = ('0' * (GENE_LENGTH - len(val))) + val   # ...everything after the prefix.
            encoded += val                                  

        elif expr.is_operator(token):
            val = bin(10 + OPERATORS.index(token))[2:]
            val = ('0' * (GENE_LENGTH - len(val))) + val
            encoded += val
        
        else:
            raise NameError('invalid symbol in encode: {symbol}'.format(symbol=token))

    return encoded
#----------------------------------------------------------------
def evaluate_fitness(chromosome, target):
    '''evaluates and sets the fitness.
       Returns _False_ if this is a solution(fitness was _NOT_ evaluated).
       Returns _True_ if not a solution(Fitness _WAS_ evaluated).
    '''
    changed = False
    decoded = decode(chromosome, symbolize_ops=True)

    # We have to look for a possible divide by zero error.
    # We look for such a pattern(a '/' followed by a 0) and then replace
    # the '/' with a '+'. This should prevent the Exception at runtime
    # without affecting the evolution of the chromosome.
    for i in xrange(len(decoded) - 1):
        if decoded[i] == '/' and decoded[i+1] == 0:
            changed = True
            decoded[i] = '+'

    # Remove trailing operators, as they obviously are meaningless.
    while decoded[-1] in OPERATORS:
        changed = True
        decoded.pop()

    # Reflect the changes in the chromosome.
    if changed:
        chromosome.bits = encode(decoded)

    try:
        val = expr.evaluate(decoded)
    except ZeroDivisionError:
        val = 99999 # A large value, making the fitness very bad.

    if val == target:
        return False

    fitness = 1.0 / abs(target - val)
    chromosome.fitness = fitness
    return True
#----------------------------------------------------------------
def roulette_select(total_fitness, population):
    fitness_slice = random() * total_fitness
    fitness_so_far = 0.0

    for phenotype in population:
        fitness_so_far += phenotype.fitness

        if fitness_so_far >= fitness_slice:
            return phenotype

    return None
#----------------------------------------------------------------
def get_random_bits(length):
    '''Return a random string of bits of given length'''
    result = ''
    for i in xrange(length):
        if random() < 0.5:
            result += '0'
        else:
            result += '1'
    
    return result
#----------------------------------------------------------------
def ga_main(target):
    soln_found = False
    population = []
    # Generate the initial population:
    for i in xrange(POP_SIZE):
        c = Chromosome(get_random_bits(CHROMO_LENGTH))
        population.append(c)

    gens_required = 0
    while(not soln_found):
        total_fitness = 0.0
        # Assign fitnesses
        for phenotype in population:
            if evaluate_fitness(phenotype, target) == False: # solution found
                print("***Solution found in {n} generations: {s} "
                      .format(n=gens_required, s=decode_as_str(phenotype)))
                soln_found = True
                break

            total_fitness += phenotype.fitness

        if soln_found:
            break
        # Create new population
        tmp = []
        cpop = 0
        while cpop < POP_SIZE:
            c1 = None
            while c1 == None:
                c1 = roulette_select(total_fitness, population)

            c2 = None
            while c2 == None:
                c2 = roulette_select(total_fitness, population)
            
            c1, c2 = copy(c1), copy(c2) # Required, as the original population will
                                        # be affected otherwise.

            crossover(c1, c2)
            mutate(c1)
            mutate(c2)
            
            tmp.append(c1)
            tmp.append(c2)

            cpop += 2

        population = tmp[:]

        gens_required += 1
        if gens_required > MAX_ALLOWABLE_GENERATIONS:
            print("***No solution found in this run!!")
            return False

    return True
#--------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    while True: # As fup says, repeat till the user gets bored!
        target = input('The target: ')
        ga_main(target)
#---------------------------------------------------------------------------------------------------


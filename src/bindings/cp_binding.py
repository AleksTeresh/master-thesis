from problem import GenericProblem
from cyclepath_classifier import classify as cpClassify
from cyclepath_classifier import Problem as CyclePathProblem
from cyclepath_classifier import Type
from cyclepath_classifier import HARD
from cyclepath_classifier import CONST as CP_CONST
from cyclepath_classifier import GLOBAL as CP_GLOBAL
from cyclepath_classifier import ITERATED_LOG as CP_ITERATED_LOG
from cyclepath_classifier import UNSOLVABLE as CP_UNSOLVABLE
from parser import parseConfigs
from config_util import normalizeConstraints, eachConstrIsHomogeneous
from util import flatten
from response import GenericResponse
from complexity import *

def classify(p: GenericProblem) -> GenericResponse:
  activeDegree = len(p.activeConstraints[0]) if len(p.activeConstraints) else 2
  passiveDegree = len(p.passiveConstraints[0]) if len(p.passiveConstraints) else 2
  leafDegree = len(p.leafConstraints[0]) if len(p.leafConstraints) else 1
  # print(activeDegree, passiveDegree, leafDegree)
  if leafDegree != 1:
    raise Exception('cyclepath', 'Leaf constraints must always be of degree 1')

  if passiveDegree != 2:
    raise Exception('cyclepath', 'Passive constraints must always be of degree 2')

  if p.isTree:
    if not eachConstrIsHomogeneous(p.activeConstraints):
      raise Exception('cyclepath', 'On trees, node constraints must be the same for all incident edges.')
  elif activeDegree != 2:
    raise Exception('cyclepath', 'In a path or cycle, passive constraints must always be of degree 2')

  problemType = Type.TREE if p.isTree else (Type.DIRECTED if p.isDirected else Type.UNDIRECTED)

  edgeConstraints = set(p.passiveConstraints)
  nodeConstraints = {} if problemType == Type.TREE else set(p.activeConstraints)
  startConstraints = {} if p.rootAllowAll else set(p.rootConstraints)
  endConstraints = {} if p.leafAllowAll else set(p.leafConstraints)

  cpProblem = CyclePathProblem(
    nodeConstraints,
    edgeConstraints,
    startConstraints,
    endConstraints,
    problemType
  )

  result = cpClassify(cpProblem)

  complexityMapping = {
    CP_CONST: CONST,
    CP_GLOBAL: GLOBAL,
    CP_ITERATED_LOG: ITERATED_LOG,
    CP_UNSOLVABLE: UNSOLVABLE
  }
  normalisedComplexity = complexityMapping[result['complexity']]

  return GenericResponse(
    p,
    normalisedComplexity,
    normalisedComplexity,
    normalisedComplexity,
    normalisedComplexity,
    result['solvable'],
    result['unsolvable']
  )
  # print('Round complexity of the problem is %s' % result['complexity'])
  # print(
  #   'Deciding the number of solvable instances is NP-complete' if
  #   result['solvable'] == HARD else
  #   'There are %s solvable instances' % result['solvable']
  # )
  # print(
  #   'Deciding the number of unsolvable instances is NP-complete' if
  #   result['unsolvable'] == HARD else
  #   'There are %s unsolvable instances' % result['unsolvable']
  # )

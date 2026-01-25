CREATE
  (python:Skill {name: "Python"}),
  (docker:Skill {name: "Docker"}),
  (k8s:Skill {name: "Kubernetes"}),
  (python)-[:PREREQUISITE_OF]->(docker),
  (docker)-[:PREREQUISITE_OF]->(k8s);
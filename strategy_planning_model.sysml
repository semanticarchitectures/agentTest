/**
 * SysML v2 Model: Air Force Strategy and Planning Process
 * Based on AFDP 3-0.1 Command and Control
 */

package StrategyAndPlanningModel {

    // Import standard libraries
    import ScalarValues::*;
    import ISQ::*;

    /**
     * Main process definition for Strategy and Planning
     */
    action def StrategyAndPlanningProcess {
        doc /*
         * Comprehensive strategy and planning process that transforms
         * strategic objectives into executable operational plans
         */

        // Input requirements
        in militaryEndStates : String[1..*];
        in nationalObjectives : String[1..*];
        in availableResources : String[1..*];

        // Output products
        out strategicPlan : StrategicPlan;
        out operationalPlans : OperationalPlan[1..*];
        out tacticalTasks : TacticalTask[1..*];

        // Sequential flow of planning activities
        first start;
        then action designActivities : DesignActivities;
        then action strategicDevelopment : StrategicDevelopment;
        then action airmanPerspectiveIntegration : IntegrateAirmanPerspective;
        then action operationalTranslation : TranslateToOperations;
        then action iterativeDesign : IterativeDesignProcess;
        then action preparation : PreparationActivities;
        then done;
    }

    /**
     * Design Activities - Provide structure and framework
     */
    action def DesignActivities {
        doc /* Creates the foundational structure and framework for operations */

        in objectives : String[1..*];
        out operationalFramework : OperationalFramework;
        out planningGuidance : PlanningGuidance;

        action provideStructure {
            doc /* Establish the operational structure */
        }

        action createFramework {
            doc /* Develop framework for guiding operations */
        }

        action guideEffectivePlanning {
            doc /* Ensure planning is effective and aligned */
        }
    }

    /**
     * Strategic Development - Work backwards from end states
     */
    action def StrategicDevelopment {
        doc /*
         * Works backwards from military and national end-states
         * to create lines of effort and operations
         */

        in endStates : String[1..*];
        in nationalObjectives : String[1..*];
        out linesOfEffort : LineOfEffort[1..*];
        out operations : Operation[1..*];

        action identifyEndStates {
            doc /* Identify desired military and national end-states */
        }

        action workBackwards {
            doc /* Reverse engineer path from end-state to present */
        }

        action createLinesOfEffort {
            doc /* Develop lines of effort to achieve objectives */
        }

        action defineOperations {
            doc /* Define operations that support lines of effort */
        }
    }

    /**
     * Airman Perspective Integration
     */
    action def IntegrateAirmanPerspective {
        doc /*
         * Incorporates the Airman's perspective to establish
         * coherent links between objectives, effects, tasks, and actions
         */

        in objectives : String[1..*];
        out linkedStructure : CoherentLinkage;

        action linkObjectivesToEffects {
            doc /* Connect objectives to desired effects */
        }

        action linkEffectsToTasks {
            doc /* Connect effects to required tasks */
        }

        action linkTasksToActions {
            doc /* Connect tasks to executable actions */
        }

        action establishCoherence {
            doc /* Ensure all links are coherent and logical */
        }
    }

    /**
     * Operational Translation
     */
    action def TranslateToOperations {
        doc /* Translates operational objectives into tactical tasks */

        in operationalObjectives : String[1..*];
        out tacticalTasks : TacticalTask[1..*];

        action analyzeObjectives {
            doc /* Analyze operational-level objectives */
        }

        action deriveTacticalTasks {
            doc /* Derive specific tactical tasks from objectives */
        }

        action assignToSubordinates {
            doc /* Assign tasks to subordinate units */
        }
    }

    /**
     * Iterative Design Process
     */
    action def IterativeDesignProcess {
        doc /*
         * Continuous assessment-informed design process
         * that builds alignment across all echelons
         */

        in assessmentData : AssessmentData[1..*];
        out refinedPlan : RefinedPlan;

        action conductAssessment {
            doc /* Perform continuous assessment of plan effectiveness */
        }

        action informDesign {
            doc /* Use assessment to inform design iterations */
        }

        action buildAlignment {
            doc /* Build alignment across all echelons */
        }

        action ensureSupport {
            doc /* Ensure activities support strategic objectives */
        }

        // Loop back for iteration
        action loop : IterativeDesignProcess;
    }

    /**
     * Preparation Activities - Bridge planning to execution
     */
    action def PreparationActivities {
        doc /* Activities that bridge planning and execution */

        in plan : StrategicPlan;
        in resources : String[1..*];
        out preparedPlan : ExecutablePlan;

        action allocateResources {
            doc /* Allocate resources to planned activities */
        }

        action refinePlan {
            doc /* Refine plan based on resource constraints */
        }

        action coordinateStakeholders {
            doc /* Coordinate with all stakeholders */
        }

        action shareInformation {
            doc /* Share information across units */
        }

        action buildTrust {
            doc /* Build trust and agreements between units */
        }
    }

    /**
     * Data structures and value types
     */

    part def StrategicPlan {
        attribute vision : String;
        attribute objectives : String[1..*];
        attribute linesOfEffort : LineOfEffort[1..*];
        attribute endState : String;
    }

    part def OperationalPlan {
        attribute operations : Operation[1..*];
        attribute resources : String[1..*];
        attribute timeline : String;
    }

    part def TacticalTask {
        attribute taskDescription : String;
        attribute assignedUnit : String;
        attribute supportingEffects : String[1..*];
    }

    part def LineOfEffort {
        attribute name : String;
        attribute objective : String;
        attribute milestones : String[1..*];
    }

    part def Operation {
        attribute operationType : String;
        attribute purpose : String;
        attribute forces : String[1..*];
    }

    part def OperationalFramework {
        attribute structure : String;
        attribute relationships : String[1..*];
    }

    part def PlanningGuidance {
        attribute principles : String[1..*];
        attribute constraints : String[1..*];
    }

    part def CoherentLinkage {
        attribute objectiveToEffectLinks : String[1..*];
        attribute effectToTaskLinks : String[1..*];
        attribute taskToActionLinks : String[1..*];
    }

    part def AssessmentData {
        attribute metrics : String[1..*];
        attribute observations : String[1..*];
        attribute recommendations : String[1..*];
    }

    part def RefinedPlan {
        attribute adjustments : String[1..*];
        attribute alignmentStatus : String;
    }

    part def ExecutablePlan {
        attribute resourceAllocations : String[1..*];
        attribute coordinationAgreements : String[1..*];
        attribute executionOrders : String[1..*];
    }

    /**
     * Requirements for the Strategy and Planning Process
     */
    requirement def StrategyPlanningRequirements {
        doc /* Requirements governing the strategy and planning process */

        requirement coherence {
            doc /* All planning elements must be coherently linked */
            subject strategyProcess : StrategyAndPlanningProcess;
        }

        requirement alignment {
            doc /* Activities must support strategic objectives and end-states */
            subject strategyProcess : StrategyAndPlanningProcess;
        }

        requirement continuousAssessment {
            doc /* Planning must be informed by continuous assessment */
            subject iterativeProcess : IterativeDesignProcess;
        }

        requirement coordinatedExecution {
            doc /* Preparation must ensure coordinated execution */
            subject preparation : PreparationActivities;
        }
    }

    /**
     * Use case: Complete Strategy and Planning Cycle
     */
    use case CompleteStrategyPlanningCycle {
        doc /*
         * Full cycle of strategy and planning from
         * national objectives to executable tactical tasks
         */

        actor AOC : String = "Air Operations Center";
        actor AFFOR : String = "Air Force Forces Staff";
        actor SubordinateUnits : String[1..*];

        use action strategyPlanning : StrategyAndPlanningProcess;

        objective createCohesivePlan {
            doc /* Create cohesive approach achieving strategic objectives */
        }
    }
}

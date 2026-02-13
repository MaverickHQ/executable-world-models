import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import * as iam from "aws-cdk-lib/aws-iam";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigwv2 from "aws-cdk-lib/aws-apigatewayv2";
import * as apigwv2Integrations from "aws-cdk-lib/aws-apigatewayv2-integrations";
import * as path from "path";

export class BeyondTokensStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const artifactsBucket = new s3.Bucket(this, "ArtifactsBucket", {
      versioned: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      enforceSSL: true,
    });

    const stateTable = new dynamodb.Table(this, "StateTable", {
      tableName: "beyond_tokens_state",
      partitionKey: { name: "state_id", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    const runsTable = new dynamodb.Table(this, "RunsTable", {
      tableName: "beyond_tokens_runs",
      partitionKey: { name: "run_id", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    const policiesTable = new dynamodb.Table(this, "PoliciesTable", {
      tableName: "beyond_tokens_policies",
      partitionKey: { name: "policy_id", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    const lambdaEnv = {
      ARTIFACT_BUCKET: artifactsBucket.bucketName,
      STATE_TABLE: stateTable.tableName,
      RUNS_TABLE: runsTable.tableName,
      POLICIES_TABLE: policiesTable.tableName,
      FIXTURE_NAME: "trading_path.json",
      ENABLE_BEDROCK_PLANNER: this.node.tryGetContext("enableBedrockPlanner") ? "1" : "0",
      BEDROCK_MODEL_ID: this.node.tryGetContext("bedrockModelId") ?? "",
    };

    const lambdaPath = path.join(__dirname, "..", "..", "..");
    const lambdaAsset = lambda.Code.fromAsset(lambdaPath, {
      exclude: [
        "infra/cdk/**",
        "**/cdk.out/**",
        "**/node_modules/**",
        "**/.venv/**",
        "**/__pycache__/**",
        "**/*.pyc",
        "**/.git/**",
        "**/.DS_Store",
        "tmp/**",
      ],
    });

    const simulateFn = new lambda.Function(this, "SimulateFn", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "services.aws.handlers.simulate_handler.handler",
      code: lambdaAsset,
      environment: lambdaEnv,
      timeout: cdk.Duration.seconds(30),
    });

    const executeFn = new lambda.Function(this, "ExecuteFn", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "services.aws.handlers.execute_handler.handler",
      code: lambdaAsset,
      environment: lambdaEnv,
      timeout: cdk.Duration.seconds(30),
    });

    const statusFn = new lambda.Function(this, "StatusFn", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "services.aws.handlers.status_handler.handler",
      code: lambdaAsset,
      environment: lambdaEnv,
      timeout: cdk.Duration.seconds(30),
    });

    const agentcoreHelloFn = new lambda.Function(this, "AgentCoreHelloFn", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "services.aws.handlers.agentcore_hello_handler.handler",
      code: lambdaAsset,
      environment: {
        ARTIFACT_BUCKET: artifactsBucket.bucketName,
      },
      timeout: cdk.Duration.seconds(10),
      reservedConcurrentExecutions: 2,
    });

    const agentcoreHelloApi = new apigwv2.HttpApi(this, "AgentCoreHelloApi", {
      apiName: "agentcore-hello",
    });

    agentcoreHelloApi.addRoutes({
      path: "/hello",
      methods: [apigwv2.HttpMethod.POST],
      integration: new apigwv2Integrations.HttpLambdaIntegration(
        "AgentCoreHelloIntegration",
        agentcoreHelloFn,
      ),
    });

    artifactsBucket.grantReadWrite(simulateFn);
    artifactsBucket.grantReadWrite(statusFn);
    artifactsBucket.grantReadWrite(executeFn);
    artifactsBucket.grantReadWrite(agentcoreHelloFn);

    stateTable.grantReadWriteData(simulateFn);
    stateTable.grantReadWriteData(executeFn);

    runsTable.grantReadWriteData(simulateFn);
    runsTable.grantReadWriteData(statusFn);
    runsTable.grantReadWriteData(executeFn);

    policiesTable.grantReadWriteData(simulateFn);

    if (this.node.tryGetContext("enableBedrockPlanner")) {
      simulateFn.addToRolePolicy(
        new iam.PolicyStatement({
          actions: ["bedrock:InvokeModel"],
          resources: ["*"],
        }),
      );
    }

    new cdk.CfnOutput(this, "ArtifactsBucketName", {
      value: artifactsBucket.bucketName,
    });
    new cdk.CfnOutput(this, "StateTableName", {
      value: stateTable.tableName,
    });
    new cdk.CfnOutput(this, "RunsTableName", {
      value: runsTable.tableName,
    });
    new cdk.CfnOutput(this, "PoliciesTableName", {
      value: policiesTable.tableName,
    });
    new cdk.CfnOutput(this, "SimulateFunctionName", {
      value: simulateFn.functionName,
    });
    new cdk.CfnOutput(this, "ExecuteFunctionName", {
      value: executeFn.functionName,
    });
    new cdk.CfnOutput(this, "StatusFunctionName", {
      value: statusFn.functionName,
    });
    new cdk.CfnOutput(this, "AgentCoreHelloFunctionName", {
      value: agentcoreHelloFn.functionName,
    });
    new cdk.CfnOutput(this, "AgentCoreHelloApiUrl", {
      value: agentcoreHelloApi.apiEndpoint,
    });
  }
}

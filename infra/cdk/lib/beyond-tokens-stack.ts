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
      encryption: s3.BucketEncryption.KMS_MANAGED,
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

    const agentcoreMemoryTable = new dynamodb.Table(this, "AgentCoreMemoryTable", {
      tableName: "beyond_tokens_agentcore_memory",
      partitionKey: { name: "pk", type: dynamodb.AttributeType.STRING },
      sortKey: { name: "sk", type: dynamodb.AttributeType.STRING },
      timeToLiveAttribute: "expires_at",
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

    const pythonDepsLayer = new lambda.LayerVersion(this, "PythonDepsLayer", {
      code: lambda.Code.fromAsset(path.join(lambdaPath, "infra", "cdk", "layers", "python-deps")),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_11],
      description: "Python dependencies for Beyond Tokens lambdas",
    });

    const simulateFn = new lambda.Function(this, "SimulateFn", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "services.aws.handlers.simulate_handler.handler",
      code: lambdaAsset,
      environment: lambdaEnv,
      timeout: cdk.Duration.seconds(30),
      reservedConcurrentExecutions: 1,
      layers: [pythonDepsLayer],
    });

    const executeFn = new lambda.Function(this, "ExecuteFn", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "services.aws.handlers.execute_handler.handler",
      code: lambdaAsset,
      environment: lambdaEnv,
      timeout: cdk.Duration.seconds(30),
      reservedConcurrentExecutions: 1,
      layers: [pythonDepsLayer],
    });

    const statusFn = new lambda.Function(this, "StatusFn", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "services.aws.handlers.status_handler.handler",
      code: lambdaAsset,
      environment: lambdaEnv,
      timeout: cdk.Duration.seconds(30),
      reservedConcurrentExecutions: 1,
      layers: [pythonDepsLayer],
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
      layers: [pythonDepsLayer],
    });

    const agentcoreToolsFn = new lambda.Function(this, "AgentCoreToolsFn", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "services.aws.handlers.agentcore_tools_handler.handler",
      code: lambdaAsset,
      environment: {
        ARTIFACT_BUCKET: artifactsBucket.bucketName,
        FIXTURE_NAME: "trading_path.json",
      },
      timeout: cdk.Duration.seconds(30),
      reservedConcurrentExecutions: 2,
      layers: [pythonDepsLayer],
    });

    const agentcoreMemoryFn = new lambda.Function(this, "AgentCoreMemoryFn", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "services.aws.handlers.agentcore_memory_handler.handler",
      code: lambdaAsset,
      environment: {
        ARTIFACT_BUCKET: artifactsBucket.bucketName,
        ENABLE_AGENTCORE_MEMORY: "1",
        AGENTCORE_MEMORY_BACKEND: "dynamodb",
        AGENTCORE_MEMORY_TABLE: agentcoreMemoryTable.tableName,
        AGENTCORE_MEMORY_TTL_SECONDS: "86400",
      },
      timeout: cdk.Duration.seconds(15),
      reservedConcurrentExecutions: 1,
      layers: [pythonDepsLayer],
    });

    const agentcoreHelloApi = new apigwv2.HttpApi(this, "AgentCoreHelloApi", {
      apiName: "agentcore-hello",
    });

    agentcoreHelloApi.addRoutes({
      path: "/agentcore/base",
      methods: [apigwv2.HttpMethod.POST],
      integration: new apigwv2Integrations.HttpLambdaIntegration(
        "AgentCoreHelloIntegration",
        agentcoreHelloFn,
      ),
    });

    agentcoreHelloApi.addRoutes({
      path: "/agentcore/tools",
      methods: [apigwv2.HttpMethod.POST],
      integration: new apigwv2Integrations.HttpLambdaIntegration(
        "AgentCoreToolsIntegration",
        agentcoreToolsFn,
      ),
    });

    agentcoreHelloApi.addRoutes({
      path: "/agentcore/memory",
      methods: [apigwv2.HttpMethod.POST],
      integration: new apigwv2Integrations.HttpLambdaIntegration(
        "AgentCoreMemoryIntegration",
        agentcoreMemoryFn,
      ),
    });

    artifactsBucket.grantReadWrite(simulateFn);
    artifactsBucket.grantReadWrite(statusFn);
    artifactsBucket.grantReadWrite(executeFn);
    artifactsBucket.grantReadWrite(agentcoreHelloFn);
    artifactsBucket.grantReadWrite(agentcoreToolsFn);
    artifactsBucket.grantReadWrite(agentcoreMemoryFn);
    agentcoreMemoryTable.grantReadWriteData(agentcoreMemoryFn);

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
    new cdk.CfnOutput(this, "AgentCoreToolsFunctionName", {
      value: agentcoreToolsFn.functionName,
    });
    new cdk.CfnOutput(this, "AgentCoreToolsApiUrl", {
      value: agentcoreHelloApi.apiEndpoint,
    });
    new cdk.CfnOutput(this, "AgentCoreMemoryFunctionName", {
      value: agentcoreMemoryFn.functionName,
    });
    new cdk.CfnOutput(this, "AgentCoreMemoryApiUrl", {
      value: agentcoreHelloApi.apiEndpoint,
    });
    new cdk.CfnOutput(this, "AgentCoreMemoryTableName", {
      value: agentcoreMemoryTable.tableName,
    });
  }
}

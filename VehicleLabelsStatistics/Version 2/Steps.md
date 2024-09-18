**English:**

---

To implement an automatic photo labeling project on AWS Console using S3, Rekognition, Lambda, and DynamoDB, you can follow these steps:

**Step 1: Create an S3 Bucket**

1. Log in to the [AWS Console](https://aws.amazon.com/console/).
2. Navigate to the **S3** service.
3. Create an S3 Bucket to store the user-uploaded photos.

**Step 2: Create a DynamoDB Table**

1. Go to DynamoDB:
    - In the AWS Console, search for “DynamoDB” and click to access it.
2. Create a table:
    - Click the “Create table” button.
    - Enter a table name, e.g., `ITrafficLabels`.
    - Set the primary key:
        - **Partition key**: `ImageName` (Type: String).
        - **Sort key**: `LabelName` (Type: String).
    - Keep other settings as default and click "Create".
3. Once the table is successfully created, you can view the detailed information on the table's page.

**Step 3: Set up Rekognition Service**

1. Integrate the Rekognition API within the Lambda function to automatically detect labels from the images.

**Step 4: Configure the Lambda Function**

1. **Lambda Trigger**: Automatically trigger the Lambda function when photos are uploaded to S3.
    - In the Lambda page, click "Create Function".
    - Choose "Author from scratch".
    - Name the function and choose **Runtime** as Python 3.x.
    - In "Permissions", select or create a role with the following permissions: `AmazonS3ReadOnlyAccess`, `AmazonRekognitionFullAccess`, `AmazonDynamoDBFullAccess`.
2. **Write Lambda Function Code**:
    - Code Logic: The Lambda function detects the S3 upload event, uses the Rekognition API to analyze the image, retrieves labels, and saves the label information into DynamoDB.
    - Refer to `LambdaFunction.py`.
3. **Configure Lambda Execution Role**:
    - Lambda needs access to Rekognition, DynamoDB, and S3. To do this, assign the appropriate IAM role:
    - Go to the IAM service, and in "Roles", create a new role.
    - Select Lambda as the trusted entity.
    - Add the following managed policies:
        - `AmazonS3ReadOnlyAccess`
        - `AmazonRekognitionReadOnlyAccess`
        - `AmazonDynamoDBFullAccess`
    - After creating the role, return to the Lambda function page, and under Configuration > Execution Role, select the newly created role.

**Step 5: Configure the S3 Trigger**

- Click the "Add Trigger" button for the Lambda function.
- Select S3 as the trigger.
- Choose the S3 bucket where the images are stored (ensure this bucket is already created).
- Set the **Event type** to "PUT", so that the Lambda function is triggered automatically whenever a new image is uploaded to S3.

**Step 6: Test the Lambda Function**

1. **Upload an Image to S3**:
    - Go to your S3 bucket and upload an image.
2. **Check DynamoDB**:
    - After the image is uploaded, the Lambda function will be triggered automatically. Go to the DynamoDB table `ImageLabelsTable` and click "Explore Table".
    - You should see the image name and the detected label data stored in the table.

**Conclusion**

1. You have created a DynamoDB table to store image labels.
2. You configured a Lambda function to automatically trigger when an image is uploaded to S3, detect the image labels using Rekognition, and store the results in DynamoDB.
3. After a successful test, you can now upload images to S3, and labels will be automatically generated and stored in DynamoDB.
4. If any issues arise during testing or actual operation, you can check the logs in Amazon CloudWatch.

---

**Chinese:**

---

在AWS Console上实现照片自动标签生成项目，使用S3、Rekognition、Lambda 和 DynamoDB，可以按照以下步骤进行：

**步骤 1: 创建 S3 Bucket**

1. 登录到 [AWS Console](https://aws.amazon.com/console/)。
2. 导航到 **S3** 服务。
3. 创建一个 S3 Bucket，用于存储用户上传的照片。

**步骤 2: 创建 DynamoDB 表**

1. 前往 DynamoDB：
    - 在 AWS 控制台中搜索“DynamoDB”，然后点击进入。
2. 创建表：
    - 点击 Create table 按钮。
    - 输入表名，比如 TrafficLabels。
    - 设置主键：
        - **Partition key**：ImageName（类型：String）。
        - **Sort key**：LabelName（类型：String）。
    - 其他设置保持默认，点击 Create。
3. 表创建成功后，在表页面，你可以查看到表的详细信息。

**步骤 3: 创建 Rekognition 服务**

1. 在 Lambda 函数中集成 Rekognition API，用于自动检测图片的标签信息。

**步骤 4: 配置 Lambda 函数**

1. **Lambda 触发器**：当照片上传到 S3 时，自动触发 Lambda 函数。
    - 在 Lambda 页面，点击 "Create Function"。
    - 选择“Author from scratch”。
    - 给函数命名，选择 **Runtime** 为 Python 3.x。
    - 在 "Permissions" 中选择或创建一个拥有以下权限的角色：`AmazonS3ReadOnlyAccess`, `AmazonRekognitionFullAccess`, `AmazonDynamoDBFullAccess`。
2. **编写 Lambda 函数代码**：
    - 代码逻辑：Lambda 函数在检测到 S3 上传事件时，通过 Rekognition API 分析图片，获取标签，并将标签信息保存到 DynamoDB。
    - 参考 `LambdaFunction.py`。
3. **配置 Lambda 的执行角色**：
    - Lambda 需要访问 Rekognition、DynamoDB 和 S3。为此，你需要分配适当的 IAM 角色：
    - 前往 IAM 服务，在 Roles 中创建一个新角色。
    - 选择 Lambda 作为信任实体。
    - 添加以下托管策略：
        - `AmazonS3ReadOnlyAccess`
        - `AmazonRekognitionReadOnlyAccess`
        - `AmazonDynamoDBFullAccess`
    - 创建角色后，返回 Lambda 函数页面，在 Configuration > Execution Role 中选择刚创建的角色。

**步骤 5: 配置 S3 触发器**

- 点击 Lambda 函数的 Add Trigger 按钮。
- 选择 S3 作为触发器。
- 在 Bucket 中选择你存储图片的 S3 存储桶（你需要提前准备好该存储桶）。
- Event type 选择 PUT，确保每当有新图像上传到 S3 时，Lambda 会自动触发。

**步骤 6: 测试 Lambda 函数**

1. 上传图像到 S3：
    - 进入你在 S3 中的存储桶，上传一张图片。
2. 查看 DynamoDB：
    - 上传图片后，Lambda 会自动触发。进入你创建的 DynamoDB 表 ImageLabelsTable，点击 Explore Table。
    - 你应该能看到图片名称和检测到的标签数据被存储在表中。

**总结**

1. 你创建了一个 DynamoDB 表用于存储图像标签。
2. 配置了一个 Lambda 函数，自动在图像上传到 S3 时触发 Rekognition，检测图像标签并存储到 DynamoDB。
3. 测试成功后，你就可以通过 S3 上传图片来实现自动标签生成，并存储在 DynamoDB 中。
4. 如果测试或实际运行中出现问题，可以前往 Amazon CloudWatch 查看 log。

---
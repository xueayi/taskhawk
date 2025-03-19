# TaskNya API 文档

## 基础信息

- 基础路径: `/api/v1`
- 响应格式: JSON
- 认证方式: 暂无

## 通用响应格式

```json
{
    "code": 200,          // 状态码
    "message": "success", // 状态信息
    "data": {            // 响应数据
        // ...
    }
}
```

## 状态码说明

- 200: 成功
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

## 任务管理接口

### 获取任务列表

GET `/api/v1/tasks`

#### 请求参数

Query 参数:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | 否 | 任务状态：pending/running/completed/warning/error |
| type | string | 否 | 任务类型：file/log/gpu |
| search | string | 否 | 搜索关键词（匹配任务名称和描述） |

#### 响应示例

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "tasks": [
            {
                "id": "task_id",
                "name": "任务名称",
                "type": "file",
                "description": "任务描述",
                "status": "running",
                "settings": {
                    // 任务特定设置
                },
                "created_at": "2024-01-01T00:00:00Z",
                "start_time": "2024-01-01T00:00:00Z",
                "elapsed": "1h 30m",
                "progress": 50
            }
        ]
    }
}
```

### 创建任务

POST `/api/v1/tasks`

#### 请求参数

```json
{
    "name": "任务名称",
    "type": "file",           // file/log/gpu
    "description": "任务描述", // 可选
    "settings": {
        // 文件监控设置
        "file_path": "/path/to/file",
        "file_pattern": "*.log",
        
        // 日志监控设置
        "log_path": "/path/to/log",
        "keywords": ["error", "warning"],
        
        // GPU监控设置
        "gpu_ids": "all",           // 或具体GPU ID: "0,1,2"
        "power_threshold": 200,      // 功耗阈值（瓦特）
        "temp_threshold": 80         // 温度阈值（°C）
    },
    "check_interval": 5,      // 检查间隔（秒）
    "auto_stop": true        // 是否自动停止
}
```

#### 响应示例

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "task": {
            "id": "task_id",
            "name": "任务名称",
            "type": "file",
            "status": "running",
            // ...其他任务信息
        }
    }
}
```

### 获取任务详情

GET `/api/v1/tasks/{task_id}`

#### 响应示例

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "task": {
            "id": "task_id",
            "name": "任务名称",
            "type": "file",
            "description": "任务描述",
            "status": "running",
            "settings": {
                // 任务特定设置
            },
            "created_at": "2024-01-01T00:00:00Z",
            "start_time": "2024-01-01T00:00:00Z",
            "elapsed": "1h 30m",
            "progress": 50,
            "metrics": {
                "timestamps": ["2024-01-01T00:00:00Z", "..."],
                "cpu": [50, 60, 70],
                "memory": [30, 35, 40],
                "gpu_util": [80, 85, 90],
                "gpu_memory": [60, 65, 70]
            },
            "logs": [
                {
                    "time": "2024-01-01T00:00:00Z",
                    "level": "INFO",
                    "message": "日志内容"
                }
            ]
        }
    }
}
```

### 停止任务

POST `/api/v1/tasks/{task_id}/stop`

#### 响应示例

```json
{
    "code": 200,
    "message": "success"
}
```

### 删除任务

DELETE `/api/v1/tasks/{task_id}`

#### 响应示例

```json
{
    "code": 200,
    "message": "success"
}
```

## 设置管理接口

### 获取系统设置

GET `/api/v1/settings`

#### 响应示例

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "settings": {
            "general": {
                "project_name": "TaskNya",
                "refresh_interval": 5,
                "language": "zh-CN"
            },
            "monitor": {
                "enable_gpu_monitor": true,
                "gpu_power_threshold": 200,
                "gpu_temp_threshold": 80,
                "enable_system_monitor": true,
                "cpu_threshold": 90,
                "memory_threshold": 90,
                "disk_threshold": 90
            },
            "notification": {
                "webhook": {
                    "enabled": true,
                    "url": "http://example.com/webhook",
                    "secret": "******"
                },
                "email": {
                    "enabled": false,
                    "smtp_server": "smtp.example.com",
                    "smtp_port": 587,
                    "smtp_username": "user@example.com",
                    "smtp_password": "******",
                    "to": "admin@example.com"
                },
                "wechat": {
                    "enabled": false,
                    "corpid": "******",
                    "corpsecret": "******",
                    "agentid": "******"
                }
            },
            "task": {
                "timeout": 30,
                "check_interval": 5,
                "auto_clean": true,
                "clean_days": 7
            },
            "system": {
                "log_level": "INFO",
                "log_file": "logs/app.log",
                "data_dir": "data",
                "debug": false
            }
        }
    }
}
```

### 更新系统设置

POST `/api/v1/settings`

#### 请求参数

```json
{
    "general": {
        "project_name": "TaskNya",
        "refresh_interval": 5,
        "language": "zh-CN"
    },
    "monitor": {
        "enable_gpu_monitor": true,
        "gpu_power_threshold": 200,
        "gpu_temp_threshold": 80,
        "enable_system_monitor": true,
        "cpu_threshold": 90,
        "memory_threshold": 90,
        "disk_threshold": 90
    },
    "notification": {
        "webhook": {
            "enabled": true,
            "url": "http://example.com/webhook",
            "secret": "******"
        },
        "email": {
            "enabled": false,
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "user@example.com",
            "smtp_password": "******",
            "to": "admin@example.com"
        },
        "wechat": {
            "enabled": false,
            "corpid": "******",
            "corpsecret": "******",
            "agentid": "******"
        }
    },
    "task": {
        "timeout": 30,
        "check_interval": 5,
        "auto_clean": true,
        "clean_days": 7
    },
    "system": {
        "log_level": "INFO",
        "log_file": "logs/app.log",
        "data_dir": "data",
        "debug": false
    }
}
```

#### 响应示例

```json
{
    "code": 200,
    "message": "success"
}
```

### 获取配置预设列表

GET `/api/v1/settings/presets`

#### 响应示例

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "presets": [
            {
                "id": "preset_id",
                "name": "预设名称",
                "description": "预设描述",
                "created_at": "2024-01-01T00:00:00Z",
                "settings": {
                    // 预设配置内容
                }
            }
        ]
    }
}
```

### 创建配置预设

POST `/api/v1/settings/presets`

#### 请求参数

```json
{
    "name": "预设名称",
    "description": "预设描述",
    "settings": {
        // 预设配置内容
    }
}
```

#### 响应示例

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "preset": {
            "id": "preset_id",
            "name": "预设名称",
            "description": "预设描述",
            "created_at": "2024-01-01T00:00:00Z",
            "settings": {
                // 预设配置内容
            }
        }
    }
}
```

### 获取预设详情

GET `/api/v1/settings/presets/{preset_id}`

#### 响应示例

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "preset": {
            "id": "preset_id",
            "name": "预设名称",
            "description": "预设描述",
            "created_at": "2024-01-01T00:00:00Z",
            "settings": {
                // 预设配置内容
            }
        }
    }
}
```

### 删除预设

DELETE `/api/v1/settings/presets/{preset_id}`

#### 响应示例

```json
{
    "code": 200,
    "message": "success"
}
``` 
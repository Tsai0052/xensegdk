#!/bin/bash

# 日志系统
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

load_config() {
    local config_file="$1"
    if [[ ! -f "$config_file" ]]; then
        log_error "配置文件不存在: $config_file"
        return 1
    fi
    
    log_info "加载配置文件: $config_file"
    
    while IFS='=' read -r key value; do
        [[ $key =~ ^[[:space:]]*# ]] && continue
        [[ -z "$key" ]] && continue
        
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs | sed 's/^"//; s/"$//')
        
        case "$key" in
            PYTHON_SCRIPT) PYTHON_SCRIPT="$value" ;;
            TASK_ID) TASK_ID="$value" ;;
            JOB_ID) JOB_ID="$value" ;;
            SN_CODE) SN_CODE="$value" ;;
            OUTPUT_ROOT) OUTPUT_ROOT="$value" ;;
            REMOTE_USER) REMOTE_USER="$value" ;;
            REMOTE_HOST) REMOTE_HOST="$value" ;;
            REMOTE_PORT) REMOTE_PORT="$value" ;;
            REMOTE_PATH_ROOT) REMOTE_PATH_ROOT="$value" ;;
            SSH_KEY) SSH_KEY="$value" ;;
            LOOP_ENABLED) LOOP_ENABLED="$value" ;;
            LOOP_INTERVAL) LOOP_INTERVAL="$value" ;;
            LOOP_COUNT) LOOP_COUNT="$value" ;;
            CLEANUP_LOCAL) CLEANUP_LOCAL="$value" ;;
            DEBUG_MODE) DEBUG_MODE="$value" ;;
            XENSEGDK)XENSEGDK="$value" ;;
            EXTRACT_TS_PYTHON_SCRIPT)EXTRACT_TS_PYTHON_SCRIPT="$value" ;;
            JSON_ONLY)JSON_ONLY="$value" ;;
            QUALITY_ANALYSIS_PYTHON_SCRIPT)QUALITY_ANALYSIS_PYTHON_SCRIPT="$value" ;;
        esac
    done < "$config_file"
}

if [["$DEBUG_MODE" == "true"]]; then
    set -x
    CONTINUE_ON_ERROR="false"
else
    set +x
    CONTINUE_ON_ERROR="true"
fi

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        *)
            log_error "未知参数: $1"
            usage
            exit 1
            ;;
    esac
done

load_config "$CONFIG_FILE"
LOCAL_FOLDER="$OUTPUT_ROOT/$TASK_ID/$JOB_ID/$SN_CODE/recording..."

# 循环状态变量
CURRENT_LOOP=0
TOTAL_SUCCESS=0
TOTAL_FAILURES=0
START_TIME=$(date +%s)

# 检查Python脚本是否存在
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    log_error "录制Python脚本不存在: $PYTHON_SCRIPT"
    exit 1
fi
if [[ ! -f "$QUALITY_ANALYSIS_PYTHON_SCRIPT" ]]; then
    log_error "数据质量分析Python脚本不存在: $QUALITY_ANALYSIS_PYTHON_SCRIPT"
    exit 1
fi
if [[ "$XENSEGDK" == "true" ]]; then
    if [[ ! -f "$EXTRACT_TS_PYTHON_SCRIPT" ]]; then
        log_error "使用H5模式，但是提取时间戳Python脚本不存在"
        exit1
    fi
fi

# 执行单次任务
execute_single_task() {
    local loop_count="$1"
    
    log_info "==================== 第 $loop_count 次任务开始 ===================="
    
    # 执行Python程序
    log_info "开始执行Python程序..."
    python3 "$PYTHON_SCRIPT" \
        --task-id "$TASK_ID" \
        --job_id "$JOB_ID" \
        --sn_code "$SN_CODE" \
        --output_root "$LOCAL_FOLDER"
    
    PYTHON_EXIT_CODE=$?
    if [[ $PYTHON_EXIT_CODE -ne 0 ]]; then
        log_error "Python程序执行失败，退出代码: $PYTHON_EXIT_CODE"
        return 1
    fi
    
    log_info "Python程序执行成功"
    
    # 检查文件保存情况
    log_info "检查生成的文件..."
    if [[ ! -d "$LOCAL_FOLDER" ]]; then
        log_error "本地文件夹不存在: $LOCAL_FOLDER"
        return 1
    fi

    while true; do
        read -p "Enter episode_id (type n for not saving): " EPISODE_ID
        
        if [[ "$EPISODE_ID" == 'n' ]]; then
            read -p "Confirm not saving (Y/n): " flag
            if [[ "$flag" == "Y" ]]; then
                rm -rf "$LOCAL_FOLDER"
                echo "Files removed"
                return
            fi
        else
            read -p "Confirm episode_id is $EPISODE_ID (Y/n): " flag
            if [[ "$flag" == "Y" ]]; then
                current_local_folder="$(dirname "$LOCAL_FOLDER")/$EPISODE_ID"
                mv "$LOCAL_FOLDER" $current_local_folder
                echo "Files saved successfully."
                break
            fi
        fi
    done
    
    # 显示生成的文件信息
    local file_count=$(find "$current_local_folder" -type f | wc -l)
    local folder_size=$(du -sh "$current_local_folder" 2>/dev/null | cut -f1 || echo "未知")
    log_info "生成文件数量: $file_count"
    log_info "文件夹大小: $folder_size"

    # 提取时间戳
    if [[ "$XENSEGDK" == "true" ]]; then
        log_info "开始从h5文件中提取时间戳..."
        python3 "$EXTRACT_TS_PYTHON_SCRIPT" \
            --h5_path_root "$current_local_folder"
    fi

    EXTRACTING_PYTHON_EXIT_CODE=$?
    if [[ $EXTRACTING_PYTHON_EXIT_CODE -ne 0 ]]; then
        log_error "提取时间戳程序执行失败，退出代码: $PYTHON_EXIT_CODE"
        return 1
    fi

    # 分析数据质量
    log_info "开始分析数据质量"
    python3 "$QUALITY_ANALYSIS_PYTHON_SCRIPT" \
        --data_root "$current_local_folder"
    
    ANALYSIS_EXIT_CODE=$?
    if [[ $ANALYSIS_EXIT_CODE -ne 0 ]]; then
            log_error "数据质量分析程序执行失败，退出代码: $PYTHON_EXIT_CODE"
        return 1
    fi

    # 构建SSH/SCP命令参数
    SSH_OPTS=""
    if [[ -n "$SSH_KEY" ]]; then
        if [[ ! -f "$SSH_KEY" ]]; then
            log_error "SSH密钥文件不存在: $SSH_KEY"
            return 1
        fi
        SSH_OPTS="-i $SSH_KEY"
    fi
    
    # 添加端口参数
    if [[ -n "$REMOTE_PORT" && "$REMOTE_PORT" != "22" ]]; then
        SSH_OPTS="$SSH_OPTS -p $REMOTE_PORT"
    fi
    
    # 测试远程服务器连接
    ssh $SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "echo 'Connection test successful'" 2>/dev/null
    if [[ $? -ne 0 ]]; then
        log_error "无法连接到远程服务器: $REMOTE_USER@$REMOTE_HOST"
        log_error "请检查网络连接、用户名、主机地址和SSH配置"
        return 1
    fi
    
    log_info "远程服务器连接测试成功"

    # 创建远程文件夹
    REMOTE_PATH="$REMOTE_PATH_ROOT/$TASK_ID/$JOB_ID/$SN_CODE/$EPISODE_ID"
    ssh $SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "[ ! -d $REMOTE_PATH ] && mkdir -p $REMOTE_PATH"

    # 使用rsync上传文件夹
    log_info "开始上传文件夹: $current_local_folder -> $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"
    RSYNC_OPTS="-avz --progress"
    if [[ -n "$SSH_KEY" || -n "$REMOTE_PORT" ]]; then
        SSH_CMD="ssh"
        if [[ -n "$SSH_KEY" ]]; then
            SSH_CMD="$SSH_CMD -i $SSH_KEY"
        fi
        if [[ -n "$REMOTE_PORT" && "$REMOTE_PORT" != "22" ]]; then
            SSH_CMD="$SSH_CMD -p $REMOTE_PORT"
        fi
        RSYNC_OPTS="$RSYNC_OPTS -e '$SSH_CMD'"
    fi

    if [[ "$JSON_ONLY" == "true" ]]; then
        # 只上传_ts.json和视频
        RSYNC_OPTS="$RSYNC_OPTS --include='*.json' --include='*.mp4' --exclude='*'"
    fi

    eval "rsync $RSYNC_OPTS '$current_local_folder/' '$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/'"
    
    UPLOAD_EXIT_CODE=$?
    if [[ $UPLOAD_EXIT_CODE -ne 0 ]]; then
        log_error "文件上传失败，退出代码: $UPLOAD_EXIT_CODE"
        return 1
    fi
    
    log_info "文件上传成功完成"
    
    # 验证上传文件
    log_info "验证上传文件..."
    local remote_file_count=$(ssh $SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "find '$REMOTE_PATH' -type f | wc -l" 2>/dev/null)
    if [[ "$remote_file_count" == "$file_count" ]]; then
        log_info "文件验证成功: 本地 $file_count 个文件，远程 $remote_file_count 个文件"
    else
        log_warn "文件数量不匹配: 本地 $file_count 个文件，远程 $remote_file_count 个文件"
    fi
    
    # 可选：清理本地文件
    if [[ "$CLEANUP_LOCAL" == "true" && $UPLOAD_EXIT_CODE -eq 0 ]]; then
        log_info "清理本地文件: $current_local_folder"
        rm -rf "$current_local_folder"
        if [[ $? -eq 0 ]]; then
            log_info "本地文件清理完成"
        else
            log_warn "本地文件清理失败"
        fi
    fi
    
    log_info "==================== 第 $loop_count 次任务完成 ===================="
    return 0
}

# 显示循环统计信息
show_loop_stats() {
    local current_time=$(date +%s)
    local elapsed_time=$((current_time - START_TIME))
    local hours=$((elapsed_time / 3600))
    local minutes=$(((elapsed_time % 3600) / 60))
    local seconds=$((elapsed_time % 60))
    
    log_info "循环统计信息:"
    log_info "  已完成循环: $CURRENT_LOOP"
    log_info "  成功次数: $TOTAL_SUCCESS"
    log_info "  失败次数: $TOTAL_FAILURES"
    log_info "  成功率: $(( TOTAL_SUCCESS * 100 / (TOTAL_SUCCESS + TOTAL_FAILURES) ))%" 
    log_info "  运行时间: ${hours}小时${minutes}分钟${seconds}秒"
    
    if [[ $LOOP_COUNT -gt 0 ]]; then
        local remaining=$((LOOP_COUNT - CURRENT_LOOP))
        log_info "  剩余循环: $remaining"
        
        if [[ $CURRENT_LOOP -gt 0 ]]; then
            local avg_time=$((elapsed_time / CURRENT_LOOP))
            local est_remaining_time=$((avg_time * remaining))
            local est_hours=$((est_remaining_time / 3600))
            local est_minutes=$(((est_remaining_time % 3600) / 60))
            log_info "  预计剩余时间: ${est_hours}小时${est_minutes}分钟"
        fi
    fi
}

# 信号处理函数
cleanup_and_exit() {
    log_warn "收到中断信号，正在停止循环..."
    show_loop_stats
    log_info "循环已停止"
    exit 130
}

# 主循环函数
main_loop() {
    log_info "开始循环执行"
    log_info "循环配置: 间隔=${LOOP_INTERVAL}秒, 次数=$([[ $LOOP_COUNT -eq 0 ]] && echo "无限" || echo "$LOOP_COUNT")"
    log_info "错误处理: $([[ "$CONTINUE_ON_ERROR" == "true" ]] && echo "遇到错误继续执行" || echo "遇到错误停止循环")"
    
    # 设置信号处理
    trap cleanup_and_exit INT TERM
    
    while true; do
        CURRENT_LOOP=$((CURRENT_LOOP + 1))
        
        log_info "开始第 $CURRENT_LOOP 次循环 ($(date '+%Y-%m-%d %H:%M:%S'))"
        
        # 执行单次任务
        if execute_single_task "$CURRENT_LOOP"; then
            TOTAL_SUCCESS=$((TOTAL_SUCCESS + 1))
            log_info "第 $CURRENT_LOOP 次循环成功完成"
        else
            TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
            log_error "第 $CURRENT_LOOP 次循环执行失败"
            
            # 根据配置决定是否继续
            if [[ "$CONTINUE_ON_ERROR" != "true" ]]; then
                log_error "遇到错误，停止循环执行"
                show_loop_stats
                exit 1
            else
                log_warn "遇到错误，但继续执行下次循环"
            fi
        fi
        
        # 显示统计信息
        show_loop_stats
        
        # 终止数据采集
        read -p "Finish collecting?(Y/n) " continue_flag
        if [[ "$continue_flag" == "Y" ]]; then
            echo "Data collection over"
            break
        fi
    done
    
    log_info "所有循环任务完成!"
    show_loop_stats
}

# 单次执行函数
single_execution() {
    log_info "执行单次任务"
    if execute_single_task "1"; then
        log_info "任务执行成功"
        
        # 可选：显示上传后的远程文件列表
        read -p "是否查看远程目录内容？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "远程目录内容:"
            ssh $SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" "ls -la '$REMOTE_PATH/'"
        fi
    else
        log_error "任务执行失败"
        exit 1
    fi
}

# 主程序入口
if [[ "$LOOP_ENABLED" == "true" ]]; then
    main_loop
else
    single_execution
fi
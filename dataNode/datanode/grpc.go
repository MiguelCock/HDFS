package datanode

import (
	"context"

	"github.com/MiguelCock/HDFS/dataNode/datanode/dngrcp"
)

func (dn *DataNode) WriteBlock(ctx context.Context, req *dngrcp.WriteBlockRequest) (*dngrcp.WriteBlockResponse, error) {
	blockID := req.GetBlockId()
	//_ := req.GetData()

	dn.Files[blockID] = FileMetadata{}
	return &dngrcp.WriteBlockResponse{Status: "Block stored successfully"}, nil
}

func (dn *DataNode) ReadBlock(ctx context.Context, req *dngrcp.ReadBlockRequest) (*dngrcp.ReadBlockResponse, error) {
	blockID := req.GetBlockId()

	_, exists := dn.Files[blockID]
	if !exists {
		return &dngrcp.ReadBlockResponse{Status: "Block not found"}, nil
	}

	return &dngrcp.ReadBlockResponse{Data: nil, Status: "Block read successfully"}, nil
}

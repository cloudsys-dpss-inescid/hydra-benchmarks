request = function()
    wrk.headers["Content-Type"] = "application/json"
    -- wrk.body = '{"name":"nativehw' .. index .. '","async":"false","cached":"true","arguments":""}'
    -- wrk.body = '{"name":"matrixmul","async":"false","cached":"true","arguments":""}'
    wrk.body = '{"name":"factors","async":"false","cached":"true","arguments":""}'
    return wrk.format("POST", nil)
end

response = function (status, headers, body)
    print("Response Body:" .. body)
end

wrk.response = response
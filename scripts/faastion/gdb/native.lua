local id = 1

function setup(thread)
    thread:set("counter", 0)
    thread:set("id", id)
    id = id + 1
end

request = function()
    local counter = wrk.thread:get("counter")
    local index = wrk.thread:get("id")

    if counter < 1 or (counter == 1 and index == 1) then
        wrk.thread:set("counter", counter + 1)
        wrk.headers["Content-Type"] = "application/json"
        wrk.body = '{"name":"nativehw' .. index .. '","async":"false","cached":"true","arguments":""}'
        return wrk.format("POST", nil)
    end

    -- If the counter has reached the limit, return nil to signal no more requests
    return nil
end

response = function (status, headers, body)
    print("Response Body:" .. body)
end

wrk.response = response
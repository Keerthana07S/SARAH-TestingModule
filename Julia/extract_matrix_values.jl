using DataTables
include("bifurcation.jl")
using Pkg
using DataFrames, Statistics

L_eq = 5
R_eq = 5
V_ref = 12
v_bus = 12
i_s = 2
C = 238
P = 5.8
R = 106
delta_t = 1.0
stability = true


function compute_r_eq()
    r_eq = 0.1:0.1:10
    l_eq = 5
    v_ref = 12
    v_bus = 12
    i_s = 2
    C = 238
    P = 5.8
    R = 106

    derivative_voltage=[]
    derivative_current=[]
    req_values=[]

    for r in r_eq
        global i_s, v_bus = runge_kutta(i_s, v_bus, l_eq, v_ref, r, C, R, P)
        dvbus = g(i_s, v_bus, C, R, P)
        dis = f(i_s, v_bus, l_eq, v_ref, r)
        push!(derivative_voltage, dvbus)
        push!(derivative_current, dis)
        push!(req_values, r)
    end

    df = DataFrame(v_prime=derivative_voltage, i_prime=derivative_current, req=req_values)
    println(df)
    cov_v = cov(df.v_prime, df.req)
    cov_i = cov(df.i_prime, df.req)
    println("Covariance btwn vbus and req: ", cov_v)
    println("Covariance btwn is and req: ", cov_i)
end

function compute_l_eq()
    l_eq = 1:0.1:10
    r_eq = 5
    v_ref = 12
    v_bus = 12
    i_s = 2
    C = 238
    P = 5.8
    R = 106

    derivative_voltage=[]
    derivative_current=[] 
    leq_values=[]

    for l in l_eq
        global i_s, v_bus = runge_kutta(i_s, v_bus, l, v_ref, r_eq, C, R, P)
        dvbus = g(i_s, v_bus, C, R, P)
        dis = f(i_s, v_bus, l, v_ref, r_eq)
        push!(derivative_voltage, dvbus)
        push!(derivative_current, dis)
        push!(leq_values, l)
    end

    df = DataFrame(v_prime=derivative_voltage, i_prime=derivative_current, leq=leq_values)
    println(df)
    cov_v = cov(df.v_prime, df.leq)
    cov_i = cov(df.i_prime, df.leq)
    println("Covariance btwn vbus and leq: ", cov_v)
    println("Covariance btwn is and leq: ", cov_i)
end

function compute_v_ref()
    v_ref = 1:0.1:12
    r_eq = 5
    l_eq = 5
    v_bus = 12
    i_s = 2
    C = 238
    P = 5.8
    R = 106

    derivative_voltage=[]
    derivative_current=[] 
    vref_values=[]

    for v in v_ref
        global i_s, v_bus = runge_kutta(i_s, v_bus, l_eq, v, r_eq, C, R, P)
        dvbus = g(i_s, v_bus, C, R, P)
        dis = f(i_s, v_bus, l_eq, v, r_eq)
        push!(derivative_voltage, dvbus)
        push!(derivative_current, dis)
        push!(vref_values, v)
    end

    df = DataFrame(v_prime=derivative_voltage, i_prime=derivative_current, vref=vref_values)
    println(df)
    cov_v = cov(df.v_prime, df.vref)
    cov_i = cov(df.i_prime, df.vref)
    println("Covariance btwn vbus and vref: ", cov_v)
    println("Covariance btwn is and vref: ", cov_i)
end

function compute_bus_voltage()
    v_bus = 1:0.1:12
    r_eq = 5
    l_eq = 5
    v_ref = 12
    i_s = 2
    C = 238
    P = 5.8
    R = 106

    derivative_voltage=[]
    derivative_current=[] 
    vbus_values=[]

    for v in v_bus
        global i_s, v_bus = runge_kutta(i_s, v, l_eq, v_ref, r_eq, C, R, P)
        dvbus = g(i_s, v, C, R, P)
        dis = f(i_s, v, l_eq, v_ref, r_eq)
        push!(derivative_voltage, dvbus)
        push!(derivative_current, dis)
        push!(vbus_values, v)
    end

    df = DataFrame(v_prime=derivative_voltage, i_prime=derivative_current, busv=vbus_values)
    println(df)
    cov_v = cov(df.v_prime, df.busv)
    cov_i = cov(df.i_prime, df.busv)
    println("Covariance btwn vbus and busv: ", cov_v)
    println("Covariance btwn is and busv: ", cov_i)
end

function compute_current()
    i_s = 0:0.1:5
    r_eq = 5
    l_eq = 5
    v_ref = 12
    v_bus = 12
    C = 238
    P = 5.8
    R = 106

    derivative_voltage=[]
    derivative_current=[] 
    is_values=[]

    for i in i_s
        global i_s, v_bus = runge_kutta(i, v_bus, l_eq, v_ref, r_eq, C, R, P)
        dvbus = g(i, v_bus, C, R, P)
        dis = f(i, v_bus, l_eq, v_ref, r_eq)
        push!(derivative_voltage, dvbus)
        push!(derivative_current, dis)
        push!(is_values, i)
    end

    df = DataFrame(v_prime=derivative_voltage, i_prime=derivative_current, curr=is_values)
    println(df)
    cov_v = cov(df.v_prime, df.curr)
    cov_i = cov(df.i_prime, df.curr)
    println("Covariance btwn vbus and curr: ", cov_v)
    println("Covariance btwn is and curr: ", cov_i)
end

function compute_capacitance()
    i_s = 2
    r_eq = 5
    l_eq = 5
    v_ref = 12
    v_bus = 12
    C = 1:0.1:1000
    P = 5.8
    R = 106

    derivative_voltage=[]
    derivative_current=[] 
    c_values=[]

    for c in C
        global i_s, v_bus = runge_kutta(i_s, v_bus, l_eq, v_ref, r_eq, c, R, P)
        dvbus = g(i_s, v_bus, c, R, P)
        dis = f(i_s, v_bus, l_eq, v_ref, r_eq)
        push!(derivative_voltage, dvbus)
        push!(derivative_current, dis)
        push!(c_values, c)
    end

    df = DataFrame(v_prime=derivative_voltage, i_prime=derivative_current, cap=c_values)
    println(df)
    cov_v = cov(df.v_prime, df.cap)
    cov_i = cov(df.i_prime, df.cap)
    println("Covariance btwn vbus and cap: ", cov_v)
    println("Covariance btwn is and cap: ", cov_i)
end

function compute_power()
    i_s = 2
    r_eq = 5
    l_eq = 5
    v_ref = 12
    v_bus = 12
    C = 238
    P = 1:0.1:10
    R = 106

    derivative_voltage=[]
    derivative_current=[] 
    p_values=[]

    for p in P
        global i_s, v_bus = runge_kutta(i_s, v_bus, l_eq, v_ref, r_eq, C, R, p)
        dvbus = g(i_s, v_bus, C, R, p)
        dis = f(i_s, v_bus, l_eq, v_ref, r_eq)
        push!(derivative_voltage, dvbus)
        push!(derivative_current, dis)
        push!(p_values, p)
    end

    df = DataFrame(v_prime=derivative_voltage, i_prime=derivative_current, pow=p_values)
    println(df)
    cov_v = cov(df.v_prime, df.pow)
    cov_i = cov(df.i_prime, df.pow)
    println("Covariance btwn vbus and pow: ", cov_v)
    println("Covariance btwn is and pow: ", cov_i)
end

function compute_resistance()
    i_s = 2
    r_eq = 5
    l_eq = 5
    v_ref = 12
    v_bus = 12
    C = 238
    P = 5.8
    R = 10:0.1:200

    derivative_voltage=[]
    derivative_current=[] 
    r_values=[]

    for r in R
        global i_s, v_bus = runge_kutta(i_s, v_bus, l_eq, v_ref, r_eq, C, r, P)
        dvbus = g(i_s, v_bus, C, r, P)
        dis = f(i_s, v_bus, l_eq, v_ref, r_eq)
        push!(derivative_voltage, dvbus)
        push!(derivative_current, dis)
        push!(r_values, r)
    end

    df = DataFrame(v_prime=derivative_voltage, i_prime=derivative_current, res=r_values)
    println(df)
    cov_v = cov(df.v_prime, df.res)
    cov_i = cov(df.i_prime, df.res)
    println("Covariance btwn vbus and res: ", cov_v)
    println("Covariance btwn is and res: ", cov_i)
end

compute_r_eq()
compute_l_eq()
compute_v_ref()
compute_bus_voltage()
compute_current()
compute_capacitance()
compute_power()
compute_resistance()

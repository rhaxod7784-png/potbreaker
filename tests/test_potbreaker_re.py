import json
from web.game import PotBreaker

def test_simulation():
    g=PotBreaker(10)
    for _ in range(2000):
        s=json.loads(g.step(.04,1,0,False,True,1,0))
        assert len(s['pots']) == 3 and 0 <= s['stacks'] <= 3
        if s['phase']!='playing': g.reset()

def test_visibility_ignores_partition():
    g=PotBreaker(1);g.walls={(9,6)};g.boss=[9,5];g.boss_face=[1,0];g.player=[9,7]
    assert g._sees_player()
    g.player=[10,5];assert not g._sees_player()
    g.player=[8,5];assert not g._sees_player()

def test_player_wall_jump_without_pot():
    g=PotBreaker(1);g.walls={(9,6)};g.player=[9,5];g.ammo=0;g.jump_stacks=1
    assert g._jump_player(0,1) and g.player==[9,7] and len(g.walls)==1

def test_boss_breach_requires_pot_and_has_cooldown():
    g=PotBreaker(4);g.boss=[9,5];g.player=[9,8];g.boss_face=[1,0];g.walls={(9,6),(9,7)};g.boss_ammo=0
    g._move_boss();assert g.boss_jump_cd==0
    g.boss=[9,5];g.boss_ammo=1;g._move_boss()
    assert g.boss_jump_cd==15 and g.boss==[9,8]

def test_pickup_immediately_replenishes():
    g=PotBreaker(13);g.ammo=0;g.player=list(g.pots[0]);g._pickups()
    assert len(g.pots)==3 and g.ammo==1

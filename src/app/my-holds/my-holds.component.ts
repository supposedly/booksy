import { Component, OnInit } from '@angular/core';

import { MemberService } from '../member.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-my-holds',
  templateUrl: './my-holds.component.html',
  styleUrls: ['./my-holds.component.css']
})
export class MyHoldsComponent implements OnInit {
  msg: string = '';
  items: any[] = [];
  cont: number = 0; // should remain unused here, I think, because one wouldn't really have so many holds/items as to require pagination

  constructor(
    public globals: Globals,
    private memberService: MemberService
  ) { }

  ngOnInit() {
    this.getHolds();
  }
  
  getHolds() {
    this.memberService.getHolds()
      .subscribe(resp => this.items = resp, err => this.msg = err.error?err.error:'Error.')
  }

}

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { MemberService } from '../member.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-personal-holds',
  templateUrl: './personal-holds.component.html',
  styleUrls: ['./personal-holds.component.css']
})
export class PersonalHoldsComponent implements OnInit {
  msg = '';
  items: any[] = [];
  cont = 0;
  uID: string;

  constructor(
    public globals: Globals,
    private memberService: MemberService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.uID = this.route.snapshot.paramMap.get('uID');
    this.getHolds(this.uID || this.globals.uID);
  }
  
  getHolds(uID) {
    this.memberService.getHolds(uID)
      .subscribe(resp => this.items = resp, err => this.msg = err.error ? err.error : 'Error.');
  }
  
  clearHold(mID) {
    this.memberService.clearHold(mID)
      .subscribe();
  }

}
